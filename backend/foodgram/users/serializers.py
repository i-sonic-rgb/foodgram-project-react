from django.contrib.auth import password_validation
from djoser.serializers import UserCreateSerializer
from foodgram.settings import (CHARFIELD_MAX_LENGTH, EMAIL_MAX_LENGTH,
                               USERNAME_MAX_LENGTH)
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import User
from .validators import validate_username


class UserSerializer(serializers.ModelSerializer):
    '''CustomUser serializer.'''
    is_subscribed = serializers.SerializerMethodField()

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

    def get_is_subscribed(self, obj):
        # Return True if requesting user is subscribed to the author.
        if (
            'request' in self.context  # Need to add this for "users/me/" url.
            and self.context['request'].user.is_authenticated
        ):
            return obj in User.objects.filter(
                following__user=self.context['request'].user
            )
        return False


class NewUserCreateSerializer(UserCreateSerializer):
    '''Serializer for creation of new CustomUser.'''
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

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'password'
        )
        # Add write_only to hash password letters.
        extra_kwargs = {'password': {'write_only': True}}
        read_only_fields = ('id',)

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserResetPasswordSerializer(serializers.ModelSerializer):
    '''Serializer for resetting password.'''
    new_password = serializers.CharField(required=True)
    current_password = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('current_password', 'new_password')
        extra_kwargs = {
            'current_password': {'write_only': True},
            'new_password': {'write_only': True},
        }

    def validate_new_password(self, value):
        password_validation.validate_password(value)
        return value
