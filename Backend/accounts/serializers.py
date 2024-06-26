from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from accounts.models import CustomUser
from django.contrib.auth import authenticate, login

class UserSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(required=True, validators=[UniqueValidator(queryset=CustomUser.objects.all())])
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)
    date_of_birth = serializers.DateField(required=False, allow_null=True)
    photo = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'phone', 'password', 'password2', 'first_name', 'last_name', 'date_of_birth', 'photo']
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        return attrs

    def create(self, validated_data):
        photo = validated_data.pop('photo', None)
        user = CustomUser.objects.create_user(
            phone=validated_data['phone'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            date_of_birth=validated_data.get('date_of_birth'),
            password=validated_data['password']
        )
        if photo:
            user.photo = photo
            user.save()
        return user
