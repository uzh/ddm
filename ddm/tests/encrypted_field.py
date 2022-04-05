from django.test import TestCase
from ddm.models import Encryption


class TestEncryptedFieldIsolated(TestCase):
    def test_encrypt_decrypt(self):
        text = 'teststring'
        enc = Encryption(secret="foo", salt="bar")
        enc_text = enc.encrypt(text)
        self.assertNotEqual(text, enc_text)
        self.assertEqual(text, enc.decrypt(enc_text))
