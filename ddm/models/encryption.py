from Crypto.Cipher import PKCS1_OAEP
from Crypto.Hash import HMAC
from Crypto.PublicKey import RSA
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
        rsa_material = RSA.importKey(self.public_key)
        cipher = PKCS1_OAEP.new(rsa_material)
        return base64.b64encode(cipher.encrypt(bytes(json.dumps(value), 'utf-8')))

    def decrypt(self, value):
        """
        Fetch encrypted data from the database, try to decode the stored data,
        None if decryption fails.
        """
        cipher = PKCS1_OAEP.new(self.rsa)
        try:
            return json.loads(cipher.decrypt(base64.b64decode(value)).decode('utf-8'))
        except binascii.Error:
            return None
