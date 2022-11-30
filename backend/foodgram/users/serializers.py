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
        if 'request' in self.context:
            return obj in User.objects.filter(
                following__user=self.context['request'].user
                )
        return False


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

    class Meta:
        model = User
        fields  = (
            'username',
            'email',
            'first_name',
            'last_name',
            'password' 
        )
        extra_kwargs = {'password': {'write_only': True}}
    
    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        print('===================')
        print(user.password)
        return user

class TokenSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ('email', )
