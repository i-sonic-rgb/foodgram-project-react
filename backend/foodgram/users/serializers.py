from djoser.serializers import UserCreateSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .validators import validate_username
from .models import User
from foodgram.settings import (
    CHARFIELD_MAX_LENGTH, EMAIL_MAX_LENGTH, USERNAME_MAX_LENGTH,
)

# class SignUpSerializer(serializers.Serializer):
#     email = serializers.EmailField(
#         max_length=EMAIL_MAX_LENGTH,
#         required=True,
#         validators=[
#             UniqueValidator(queryset=User.objects.all())])
#     username = serializers.CharField(
#         max_length=USERNAME_MAX_LENGTH,
#         required=True,
#         validators=[
#             validate_username, UniqueValidator(queryset=User.objects.all())])

#     class Meta:
#         fields = ('username', 'email')


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.CharField(
        max_length=USERNAME_MAX_LENGTH, default = 'false'
    )
    
    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_subscribed'
        )

class NewUserCreateSerializer(UserCreateSerializer):
    username = serializers.CharField(
        max_length=USERNAME_MAX_LENGTH,
        required=True,
        validators=[
            validate_username, UniqueValidator(queryset=User.objects.all())]
    )
    email = serializers.EmailField(
        max_length=EMAIL_MAX_LENGTH,
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    first_name = serializers.CharField(
        max_length=CHARFIELD_MAX_LENGTH,
        required=True
    )
    last_name = serializers.CharField(
        max_length=CHARFIELD_MAX_LENGTH,
        required=True
    )
    password = serializers.CharField(
        max_length=CHARFIELD_MAX_LENGTH,
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields  = (
            'username',
            'email',
            'first_name',
            'last_name',
            'password' 
        )

# class TokenSerializer(serializers.ModelSerializer):
#     username = serializers.CharField(required=True)
#     confirmation_code = serializers.CharField(required=True)

#     class Meta:
#         model = User
#         fields = ('username', 'confirmation_code')
