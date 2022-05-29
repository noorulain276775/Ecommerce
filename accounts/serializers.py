from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from accounts.models import CustomUser


class UserSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(required=True,
            validators=[UniqueValidator(queryset=CustomUser.objects.all())]
            )
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'phone', 'username', 'password', 'password2','first_name', 'last_name', 'date_of_birth']
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True}
        }


    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        return attrs

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            phone=validated_data['phone'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            username=validated_data['username'],
            date_of_birth=validated_data['date_of_birth'],
            password= (validated_data['password'])
        )

        return user