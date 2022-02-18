from django.models import TextField
from django.conf import settings
from django.core import signing
from base64 import b64decode, b64encode


class EncryptedField(TextField):
    class JSONSerializer:
        def dumps(self, obj):
            return json.dumps(obj, separators=(",", ":")).encode("latin-1")
        def loads(self, data):
            return json.loads(data.decode("latin-1"))

    """ This Field encrypts data using symmetric encryption and stores the output as BASE64 in a TextField """

    description = "Store data in an encrypted field"  


    def __init__(self, *args, **kwargs):
        """
        Besides the 'regular' TextField options, there are 3 things to note:
        1st: blank and null are True by default
        2nd: if a 'secret' is specified it will be used for encryption, otherwise the settings SECRET_KEY
        """
        kwargs['blank'] = True
        kwargs['null'] = True
        salt = settings.SALT_VALUE if hasattr(settings, 'SALT_VALUE') else ''
        self.signer = signing.TimestampSigner(key=settings.SECRET_KEY, salt=salt) if 'secret' not in kwargs else signing.TimestampSigner(key=kwargs['secret'], salt=salt)
        super().__init__(*args, **kwargs)  

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs["blank"]
        del kwargs["null"]
        return name, path, args, kwargs  
    
    def get_prep_value(self, value):
        return b64encode(self.signer.sign_object(value, serializer=JSONSerializer, compress=True)) 
    
    def from_db_value(self, value, expression, connection):
        return b64decode(self.signer.unsign_object(value, serializer=JSONSerializer, compress=True)) if value else None
    
    def to_python(self, value):
        return b64decode(self.signer.unsign_object(value, serializer=JSONSerializer, compress=True)) if value else None
