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


class UserRegistrationView(generics.CreateAPIView):
    
    permission_classes = (permissions.AllowAny,)
    
    serializer_class = UserSerializer
    queryset = CustomUser.objects.all()
    
class LoginView(APIView):
    
    permission_classes = (permissions.AllowAny,)

    def post(self,request):
        phone = request.data.get('phone')
        password = request.data.get('password')
        
        if phone and password:
            user = authenticate(request, phone=phone, password=password)
            if user is not None:
                login(request, user)
                return Response({"message": "Your are logged In!"}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Either phone number or password is wrong!"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "Please type again!"}, status=status.HTTP_400_BAD_REQUEST)       
        

