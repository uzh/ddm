from django.models import TextField
from django.conf import settings

from Crypto.Cipher import PKCS1_OAEP
from Crypto.Hash import HMAC
from Crypto.PublicKey import RSA
from struct import pack

import binascii
import base64


class EncryptedField(TextField):
    class JSONSerializer:
        def dumps(self, obj):
            return json.dumps(obj, separators=(",", ":")).encode("latin-1")
        def loads(self, data):
            return json.loads(data.decode("latin-1"))

    """ This Field encodes data as JSON and uses deterministic RSA to encrypt the data the output as BASE64 in a TextField """

    description = "Store data in an encrypted field"

    def __init__(self, *args, **kwargs):
        """
        Besides the 'regular' TextField options, there are 3 things to note:
        1st: blank and null are True by default
        2nd: if a 'secret' is specified it will be used for encryption/decryption, otherwise the settings SECRET_KEY
        3rd: a 'salt' must be specified, it will be used for encryption/decryption, this should be unique per project
        4th: a 'public_key' may be specified, it will be used for encryption instead of generating the key dynamically
        """
        kwargs['blank'] = True
        kwargs['null'] = True
        self.counter = 0
        self.secret = kwargs['secret'] if 'secret' in kwargs else settings.SECRET_KEY
        self.salt = kwargs['salt']
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs['blank']
        del kwargs['null']
        if 'secret' in kwargs:
            del kwargs['secret']
        del kwargs['salt']
        del self.counter
        del self.secret
        del self.salt
        return name, path, args, kwargs

    def get_prep_value(self, value):
        """ save encrypted data to the database, either use a supplied 'public_key' or generate the material dynamically  """
        rsa_material = self._generate() if 'public_key' not in kwargs else RSA.importKey(kwargs['public_key'])
		cipher = PKCS1_OAEP.new(rsa_key)
			message = str.encode(message)
		return base64.b64encode(cipher.encrypt(JSONSerializer().dumps(value)))

    def from_db_value(self, value, expression, connection):
        """ fetch encrypted data from the database, try to decode the stored data, None if decryption fails """
		rsa_material = self._generate()
		cipher = PKCS1_OAEP.new(rsa_key)
		try:
			return JSONSerializer().loads(acipher.decrypt(base64.b64decode(value)))
		except binascii.Error:
			return None

    def to_python(self, value):
        """ fetch encrypted data from the database, try to decode the stored data, None if decryption fails """
		rsa_material = self._generate()
		cipher = PKCS1_OAEP.new(rsa_key)
		try:
			return JSONSerializer().loads(acipher.decrypt(base64.b64decode(value)))
		except binascii.Error:
			return None

    def fetch_public(self):
        """ retrieve the public key of the generated encryption material """
        return self._generate().publickey()

	def _generate(self):
		seed_128 = HMAC.new(bytes(self.secret, 'utf-8') + bytes(self.salt, 'utf-8')).digest()
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
		return RSA.generate(2048, randfunc=PRNG(seed_128))

