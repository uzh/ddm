import base64
import json

from io import BytesIO
from struct import pack

from django.db import models
from django.views.decorators.debug import sensitive_variables

from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Hash import HMAC
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes


class ModelWithEncryptedData(models.Model):

    class Meta:
        abstract = True

    @sensitive_variables()
    def save(self, *args, **kwargs):

        if 'encryptor' in kwargs:
            encryptor = kwargs.pop('encryptor')
        else:
            secret = kwargs['secret'] if 'secret' in kwargs else self.project.secret_key
            encryptor = Encryption(secret, self.project.get_salt(), self.project.public_key)

        # Prevent double encryption.
        try:
            self.data = encryptor.encrypt(self.data)
        except TypeError:
            pass
        super().save(*args, **kwargs)

    @sensitive_variables()
    def get_decrypted_data(self, secret, salt, decryptor=None):
        try:
            if decryptor:
                return decryptor.decrypt(self.data)
            else:
                return Decryption(secret, salt).decrypt(self.data)
        except ValueError as e:
            raise ValueError(f'Wrong secret, {e}')


class PRNG(object):
    def __init__(self, seed):
        self.index = 0
        self.seed = seed
        self.buffer = b""

    def __call__(self, n):
        while len(self.buffer) < n:
            self.buffer += HMAC.new(self.seed + pack("<I", self.index)).digest()
            self.index += 1
        result, self.buffer = self.buffer[:n], self.buffer[n:]
        return result


class AsyncSyncCrypto:
    @staticmethod
    def get_public_key(secret, salt):
        return Encryption.get_rsa(secret, salt).publickey().exportKey()

    @staticmethod
    def get_rsa(secret, salt):
        if secret is None:
            raise ValueError('secret is None.')
        if salt is None:
            raise ValueError('salt is None.')
        seed_128 = HMAC.new(bytes(secret, 'utf-8') + bytes(salt, 'utf-8')).digest()
        return RSA.generate(2048, randfunc=PRNG(seed_128))


class Encryption(AsyncSyncCrypto):

    def __init__(self, secret=None, salt=None, public=None):
        if public:
            self.public_key = public
        else:
            self.public_key = self.get_public_key(secret, salt)

    def encrypt(self, value):
        """
        Save encrypted data to the database, either use a supplied 'public_key'
        or generate the material dynamically.
        """
        session_key = get_random_bytes(16)
        cipher_aes = AES.new(session_key, AES.MODE_EAX)
        cipher_data, tag = cipher_aes.encrypt_and_digest(bytes(json.dumps(value), 'utf-8'))
        cipher_rsa = PKCS1_OAEP.new(RSA.importKey(self.public_key))
        encrypted_session_key = cipher_rsa.encrypt(session_key)
        payload = encrypted_session_key + cipher_aes.nonce + tag + cipher_data
        return base64.encodebytes(payload)


class Decryption(AsyncSyncCrypto):

    def __init__(self, secret, salt):
        self.rsa = self.get_rsa(secret, salt)

    def decrypt(self, value):
        """
        Fetch encrypted data from the database, try to decode the stored data,
        None if decryption fails.
        """
        value_bytes = BytesIO(base64.decodebytes(value))
        encrypted_session_key = value_bytes.read(self.rsa.size_in_bytes())
        nonce = value_bytes.read(16)
        tag = value_bytes.read(16)
        cipher_data = value_bytes.read()
        session_key = PKCS1_OAEP.new(self.rsa).decrypt(encrypted_session_key)
        cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
        decrypted = cipher_aes.decrypt_and_verify(cipher_data, tag)
        return json.loads(decrypted.decode('utf-8'))
