from accounts.models import CustomUser
from accounts.serializers import *
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.contrib.auth import authenticate, login
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, BasicAuthentication

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
        
class ChangePasswordView(generics.UpdateAPIView):
    
    serializer_class = ChangePasswordSerializer
    model = CustomUser
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj
    
    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            response = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'message': 'Password updated successfully',
                'data': []
            }
            return Response(response)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
