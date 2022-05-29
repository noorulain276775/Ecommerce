from accounts.models import CustomUser
from accounts.serializers import UserSerializer
from rest_framework import generics


class UserRegistrationView(generics.CreateAPIView):

    serializer_class = UserSerializer
    queryset = CustomUser.objects.all()
