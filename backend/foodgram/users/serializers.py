from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from validators import validate_username
from models import User
from foodgram.settings import EMAIL_MAX_LENGTH, USERNAME_MAX_LENGTH

class SignUpSerializer(serializers.Serializer):
    email = serializers.EmailField(
        max_length=EMAIL_MAX_LENGTH,
        required=True,
        validators=[
            UniqueValidator(queryset=User.objects.all())])
    username = serializers.CharField(
        max_length=USERNAME_MAX_LENGTH,
        required=True,
        validators=[
            validate_username, UniqueValidator(queryset=User.objects.all())])

    class Meta:
        fields = ('username', 'email')


class UserSerializer(serializers.ModelSerializer):
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

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'role'
        )


class TokenSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('username', 'confirmation_code')
