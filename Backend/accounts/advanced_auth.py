import random
import string
from django.core.cache import cache
from django.contrib.auth.hashers import make_password
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate
from django.utils import timezone
from datetime import timedelta
import jwt
from django.conf import settings
from .models import CustomUser
from .serializers import UserSerializer
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
import logging

logger = logging.getLogger(__name__)

def generate_otp():
    """Generate a 6-digit OTP"""
    return ''.join(random.choices(string.digits, k=6))

def generate_jwt_tokens(user):
    """Generate access and refresh tokens"""
    payload = {
        'user_id': user.id,
        'phone': user.phone,
        'exp': timezone.now() + timedelta(hours=1),  # Access token expires in 1 hour
        'iat': timezone.now(),
        'type': 'access'
    }
    
    refresh_payload = {
        'user_id': user.id,
        'exp': timezone.now() + timedelta(days=7),  # Refresh token expires in 7 days
        'iat': timezone.now(),
        'type': 'refresh'
    }
    
    access_token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    refresh_token = jwt.encode(refresh_payload, settings.SECRET_KEY, algorithm='HS256')
    
    return access_token, refresh_token

class AdvancedRegisterView(APIView):
    permission_classes = [AllowAny]
    
    @method_decorator(ratelimit(key='ip', rate='5/m', method='POST'))
    def post(self, request):
        try:
            serializer = UserSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                access_token, refresh_token = generate_jwt_tokens(user)
                
                logger.info(f"User registered successfully: {user.phone}")
                
                return Response({
                    'message': 'User registered successfully',
                    'user': UserSerializer(user).data,
                    'access_token': access_token,
                    'refresh_token': refresh_token
                }, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            return Response({'error': 'Registration failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AdvancedLoginView(APIView):
    permission_classes = [AllowAny]
    
    @method_decorator(ratelimit(key='ip', rate='10/m', method='POST'))
    def post(self, request):
        try:
            phone = request.data.get('phone')
            password = request.data.get('password')
            
            if not phone or not password:
                return Response({'error': 'Phone and password are required'}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
            user = authenticate(request, phone=phone, password=password)
            if user:
                access_token, refresh_token = generate_jwt_tokens(user)
                
                logger.info(f"User logged in successfully: {user.phone}")
                
                return Response({
                    'message': 'Login successful',
                    'user': UserSerializer(user).data,
                    'access_token': access_token,
                    'refresh_token': refresh_token
                }, status=status.HTTP_200_OK)
            else:
                logger.warning(f"Failed login attempt for phone: {phone}")
                return Response({'error': 'Invalid credentials'}, 
                              status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return Response({'error': 'Login failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TokenRefreshView(APIView):
    permission_classes = [AllowAny]
    
    @method_decorator(ratelimit(key='ip', rate='20/m', method='POST'))
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            
            if not refresh_token:
                return Response({'error': 'Refresh token is required'}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
            # Check if token is blacklisted
            if cache.get(f'blacklisted_token_{refresh_token}'):
                return Response({'error': 'Token has been revoked'}, 
                              status=status.HTTP_401_UNAUTHORIZED)
            
            try:
                payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=['HS256'])
                
                if payload.get('type') != 'refresh':
                    return Response({'error': 'Invalid token type'}, 
                                  status=status.HTTP_401_UNAUTHORIZED)
                
                user = CustomUser.objects.get(id=payload['user_id'])
                access_token, new_refresh_token = generate_jwt_tokens(user)
                
                # Blacklist old refresh token
                cache.set(f'blacklisted_token_{refresh_token}', True, 
                         timeout=int((payload['exp'] - timezone.now()).total_seconds()))
                
                logger.info(f"Token refreshed for user: {user.phone}")
                
                return Response({
                    'access_token': access_token,
                    'refresh_token': new_refresh_token
                }, status=status.HTTP_200_OK)
                
            except jwt.ExpiredSignatureError:
                return Response({'error': 'Refresh token has expired'}, 
                              status=status.HTTP_401_UNAUTHORIZED)
            except jwt.InvalidTokenError:
                return Response({'error': 'Invalid refresh token'}, 
                              status=status.HTTP_401_UNAUTHORIZED)
            except CustomUser.DoesNotExist:
                return Response({'error': 'User not found'}, 
                              status=status.HTTP_401_UNAUTHORIZED)
                
        except Exception as e:
            logger.error(f"Token refresh error: {str(e)}")
            return Response({'error': 'Token refresh failed'}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            # Get tokens from request headers
            auth_header = request.META.get('HTTP_AUTHORIZATION')
            if auth_header and auth_header.startswith('Bearer '):
                access_token = auth_header.split(' ')[1]
                
                # Blacklist the access token
                try:
                    payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=['HS256'])
                    cache.set(f'blacklisted_token_{access_token}', True, 
                             timeout=int((payload['exp'] - timezone.now()).total_seconds()))
                except:
                    pass
            
            # Also blacklist refresh token if provided
            refresh_token = request.data.get('refresh_token')
            if refresh_token:
                try:
                    payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=['HS256'])
                    cache.set(f'blacklisted_token_{refresh_token}', True, 
                             timeout=int((payload['exp'] - timezone.now()).total_seconds()))
                except:
                    pass
            
            logger.info(f"User logged out: {request.user.phone}")
            
            return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            return Response({'error': 'Logout failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            serializer = UserSerializer(request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Profile fetch error: {str(e)}")
            return Response({'error': 'Failed to fetch profile'}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def put(self, request):
        try:
            serializer = UserSerializer(request.user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                logger.info(f"Profile updated for user: {request.user.phone}")
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Profile update error: {str(e)}")
            return Response({'error': 'Profile update failed'}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)
