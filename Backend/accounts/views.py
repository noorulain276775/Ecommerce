from sqlite3 import Cursor
from django.forms import ValidationError
from accounts.models import CustomUser
from accounts.serializers import *
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.contrib.auth import authenticate, login
from rest_framework import status
from .tokenAuthentication import JWTAuthentication
from rest_framework.exceptions import ValidationError as DRFValidationError
import random
import string
from django.core.cache import cache
from django.contrib.auth.hashers import make_password

class UserRegistrationView(generics.CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserSerializer
    queryset = CustomUser.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except ValidationError as e:
            return Response({'error': e.messages}, status=status.HTTP_400_BAD_REQUEST)
        except DRFValidationError as e:
            return Response({'error': e.detail}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):

    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        phone = request.data.get('phone')
        password = request.data.get('password')

        if phone and password:
            user = authenticate(request, phone=phone, password=password)
            if user is not None:
                payload = {
                    "phone": user.phone,
                    "id": user.id
                }
                token = JWTAuthentication.generate_token(payload=payload)
                return Response({
                    "message": "Login Successful",
                    'token': token,
                    'user': payload
                }, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Either phone number or password is wrong!"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "Please type again!"}, status=status.HTTP_400_BAD_REQUEST)


def generate_otp():
    """Generate a 6-digit OTP"""
    return ''.join(random.choices(string.digits, k=6))


class ForgotPasswordView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        phone = request.data.get('phone')
        
        if not phone:
            return Response({"message": "Phone number is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = CustomUser.objects.get(phone=phone)
        except CustomUser.DoesNotExist:
            return Response({"message": "User with this phone number does not exist"}, status=status.HTTP_404_NOT_FOUND)
        
        # Generate OTP
        otp = generate_otp()
        
        # Store OTP in cache with 5-minute expiry
        cache_key = f"otp_{phone}"
        cache.set(cache_key, otp, 300)  # 5 minutes
        
        # In a real application, you would send this OTP via SMS
        # For now, we'll just return it in the response for testing
        print(f"OTP for {phone}: {otp}")  # Remove this in production
        
        return Response({
            "message": "OTP sent successfully",
            "otp": otp  # Remove this in production
        }, status=status.HTTP_200_OK)


class VerifyOTPView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        phone = request.data.get('phone')
        otp = request.data.get('otp')
        
        if not phone or not otp:
            return Response({"message": "Phone number and OTP are required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get OTP from cache
        cache_key = f"otp_{phone}"
        stored_otp = cache.get(cache_key)
        
        if not stored_otp:
            return Response({"message": "OTP has expired or is invalid"}, status=status.HTTP_400_BAD_REQUEST)
        
        if stored_otp != otp:
            return Response({"message": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)
        
        # OTP is valid, mark phone as verified
        verification_key = f"verified_{phone}"
        cache.set(verification_key, True, 600)  # 10 minutes
        
        return Response({
            "message": "OTP verified successfully"
        }, status=status.HTTP_200_OK)


class ResendOTPView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        phone = request.data.get('phone')
        
        if not phone:
            return Response({"message": "Phone number is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = CustomUser.objects.get(phone=phone)
        except CustomUser.DoesNotExist:
            return Response({"message": "User with this phone number does not exist"}, status=status.HTTP_404_NOT_FOUND)
        
        # Generate new OTP
        otp = generate_otp()
        
        # Store OTP in cache with 5-minute expiry
        cache_key = f"otp_{phone}"
        cache.set(cache_key, otp, 300)  # 5 minutes
        
        # In a real application, you would send this OTP via SMS
        print(f"New OTP for {phone}: {otp}")  # Remove this in production
        
        return Response({
            "message": "OTP resent successfully",
            "otp": otp  # Remove this in production
        }, status=status.HTTP_200_OK)


class ResetPasswordView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        phone = request.data.get('phone')
        password = request.data.get('password')
        
        if not phone or not password:
            return Response({"message": "Phone number and password are required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if phone is verified
        verification_key = f"verified_{phone}"
        if not cache.get(verification_key):
            return Response({"message": "Phone number not verified"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = CustomUser.objects.get(phone=phone)
        except CustomUser.DoesNotExist:
            return Response({"message": "User with this phone number does not exist"}, status=status.HTTP_404_NOT_FOUND)
        
        # Update password
        user.password = make_password(password)
        user.save()
        
        # Clear verification cache
        cache.delete(verification_key)
        
        return Response({
            "message": "Password reset successfully"
        }, status=status.HTTP_200_OK)
