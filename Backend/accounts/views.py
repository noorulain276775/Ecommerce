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
