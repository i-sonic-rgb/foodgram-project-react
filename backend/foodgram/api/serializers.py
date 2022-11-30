from django.core.validators import MinValueValidator
from rest_framework import serializers
from rest_framework.validators import UniqueValidator


from .models import Ingridient, Recipe, RecipeIngridient, User
from users.serializers import UserSerializer
from foodgram.settings import (
    CHARFIELD_MAX_LENGTH, EMAIL_MAX_LENGTH, USERNAME_MAX_LENGTH,
)


class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(many=False)
    tags = serializers.SlugRelatedField(
        slug_field='name',
        read_only=True,
    )
    image = serializers.CharField()
    cooking_time = serializers.FloatField(
        validators=[MinValueValidator(1), ]
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'author',
            'image',
            'text',
            'ingridients',
            'tags',
            'cooking_time'
        )
