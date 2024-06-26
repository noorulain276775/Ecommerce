import jwt
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
from datetime import datetime, timedelta


"""To implement a custom authentication scheme, we need to 
subclass the DRF's BaseAuthentication and override the .authenticate(self, request) 
method.

"""

class JWTAuthentication(BaseAuthentication):

    @staticmethod
    def generate_token(payload):
        expiration = datetime.now() + timedelta(hours=24)
        # Unix timestamp is a system for tracking time in computing
        payload['expiration']= expiration.timestamp()
        token = jwt.encode(payload, key=settings.SECRET_KEY, algorithm="HS256")
        return token

