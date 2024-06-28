import jwt
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
from django.contrib.auth.models import User
from datetime import datetime, timedelta

class JWTAuthentication(BaseAuthentication):

    @staticmethod
    def generate_token(payload):
        expiration = datetime.now() + timedelta(hours=24)
        payload['exp'] = expiration.timestamp()  # Use 'exp' for JWT standard expiration claim
        token = jwt.encode(payload, key=settings.SECRET_KEY, algorithm="HS256")
        return token

    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        print(auth_header)
        if not auth_header:
            return None

        try:
            token_type, token = auth_header.split()
            if token_type.lower() != 'bearer':
                raise AuthenticationFailed('Invalid token type')
            
            decoded_payload = jwt.decode(token, key=settings.SECRET_KEY, algorithms=["HS256"])
            expiration = datetime.fromtimestamp(decoded_payload['exp'])
            
            if expiration < datetime.now():
                raise AuthenticationFailed('Token has expired')
            
            user_id = decoded_payload.get('id')
            if not user_id:
                raise AuthenticationFailed('Invalid token payload')
            
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                raise AuthenticationFailed('User not found')
            
            return (user, token)
        
        except (InvalidTokenError, ExpiredSignatureError) as e:
            raise AuthenticationFailed(f'Token error: {str(e)}')
        except Exception as e:
            raise AuthenticationFailed(f'Authentication error: {str(e)}')

