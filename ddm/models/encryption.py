from Crypto.Cipher import PKCS1_OAEP
from Crypto.Hash import HMAC
from Crypto.PublicKey import RSA
from io import BytesIO
from struct import pack

import binascii
import base64
import json


class Encryption:

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

    def __init__(self, secret=None, salt=None, public_key=None):
        self.counter = 0
        if public_key:
            self.public_key = public_key
        else:
            seed_128 = HMAC.new(bytes(secret, 'utf-8') + bytes(salt, 'utf-8')).digest()
            self.rsa = RSA.generate(2048, randfunc=Encryption.PRNG(seed_128))
            self.public_key = self.rsa.publickey().exportKey()

    def encrypt(self, value):
        """
        Save encrypted data to the database, either use a supplied 'public_key'
        or generate the material dynamically.
        """
        session_key = get_random_bytes(16)
        cipher_aes = AES.new(session_key, AES.MODE_EAX)
        cipher_data, tag = cipher_aes.encrypt_and_digest(bytes(json.dumps(value), 'utf-8')
        cipher_rsa  = PKCS1_OAEP.new(RSA.importKey(self.public_key))
        encrypted_session_key = cipher_rsa.encrypt(session_key)
        payload = encrypted_session_key + cipher_aes.nonce + tag + cipher_data
        return base64.encodebytes(payload)

    def decrypt(self, value):
        """
        Fetch encrypted data from the database, try to decode the stored data,
        None if decryption fails.
        """
        value_bytes = BytesIO(base64.decodebytes(value))
        encrypted_session_key = value_bytes.read(self.rsa.size_in_bytes())
        nonce = value_bytes.read(16)
        tag = value_bytes.read(16)
        cipherdata = encrypted_bytes.read()
        session_key = PKCS1_OAEP.new(self.rsa.exportKey()).decrypt(encrypted_session_key)
        cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
        decrypted = cipher_aes.decrypt_and_verify(cipherdata, tag)
        return json.loads(decrypted).decode('utf-8')

