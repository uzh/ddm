from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Hash import HMAC
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from django.db import models
from io import BytesIO
from struct import pack

import base64
import json

from django.views.decorators.debug import sensitive_variables


class ModelWithEncryptedData(models.Model):

    secret = None
    encryption = None
    decryption = None

    class Meta:
        abstract = True

    @sensitive_variables()
    def extract_secret(self, **kwargs):
        if 'secret' in kwargs and not self.secret:
            return kwargs['secret'], True
        elif 'secret' not in kwargs and not self.secret:
            return self.project.secret_key, True
        elif 'secret' in kwargs and self.secret and self.secret != kwargs['secret']:
            return kwargs['secret'], True
        else:
            return self.project.secret_key, False

    @sensitive_variables()
    def encrypt(self, value, **kwargs):
        self.secret, forced = self.extract_secret(**kwargs)
        if not self.encryption or forced:
            self.encryption = Encryption(self.secret, str(self.project.date_created), self.project.public_key)
        return self.encryption.encrypt(value)

    @sensitive_variables()
    def decrypt(self, value, **kwargs):
        self.secret, forced = self.extract_secret(**kwargs)
        if not self.decryption or forced:
            self.decryption = Decryption(self.secret, str(self.project.date_created))
        return self.decryption.decrypt(value)

    @sensitive_variables()
    def save(self, *args, **kwargs):
        self.data = self.encrypt(self.data, **kwargs)
        super().save(*args, **kwargs)

    @sensitive_variables()
    def get_decrypted_data(self, *args, **kwargs):
        if self.project.super_secret and 'secret' not in kwargs:
            raise KeyError('Super secret project expects the custom secret to be passed in kwargs["secret"].')

        try:
            return self.decrypt(self.data, **kwargs)
        except ValueError as e:
            print(e)
            raise ValueError('Wrong secret.')


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
