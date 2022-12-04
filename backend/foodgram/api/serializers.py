from django.core.validators import MinValueValidator, MinLengthValidator
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.shortcuts import get_object_or_404
from rest_framework.response import Response

from .models import Ingridient, Recipe, RecipeIngridient, RecipeTag, Tag, User
from users.models import Subscription
from users.serializers import UserSerializer
from foodgram.settings import (
    CHARFIELD_MAX_LENGTH, EMAIL_MAX_LENGTH, USERNAME_MAX_LENGTH,
)


class RecipeIngidientSerializer(serializers.Serializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingridient.objects.all(), required=True
    )
    name = serializers.ReadOnlyField(source='ingridient_id.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingridient_id.measurement_unit'
    )
    amount = serializers.IntegerField(
        required=True, validators=[MinValueValidator(1),]
    )

    class Meta:
        model = RecipeIngridient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(many=False, read_only=True)
    image = serializers.CharField(required=True)
    cooking_time = serializers.IntegerField(required=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    ingridients = RecipeIngidientSerializer(
        many=True, required=True, source='recipeingridient_set'
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True, required=True,
        validators=[MinLengthValidator(1),])

    class Meta:
        model = Recipe
        fields = (
            'id',
            'author',
            'image',
            'name',
            'text',
            'ingridients',
            'tags',
            'cooking_time',
            'is_favorited',
            'is_in_shopping_cart'
        )

    def get_is_favorited(self, obj):
        if (
            'request' in self.context
            and self.context['request'].user.is_authenticated
        ):
            return obj in Recipe.objects.filter(
                favorites__user=self.context['request'].user
            )
        return False

    def get_is_in_shopping_cart(self, obj):
        if (
            'request' in self.context
            and self.context['request'].user.is_authenticated
        ):
            return obj in Recipe.objects.filter(
                in_shopping_cart__user=self.context['request'].user
            )
        return False
    
    def validate_tags(self, value):
        if len(value) == 0:
            raise serializers.ValidationError('at least one tag required!')
        return value
    
    def validate_ingridients(self, value):
        if len(value) == 0:
            raise serializers.ValidationError(
                'at least one ingridient required!'
            )
        return value

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingridients = validated_data.pop('recipeingridient_set')
        
        instance = Recipe.objects.create(
            author=self.context['request'].user,
            **validated_data
        )

        for tag in tags:
            tag_instance=RecipeTag.objects.create(
                tag_id=tag,
                recipe_id=instance
            )
            tag_instance.save()

        for ingridient in ingridients:
            ri = RecipeIngridient(
                ingridient_id=ingridient['id'],
                recipe_id=instance,
                amount=ingridient['amount']
            )
            ri.save()
        instance.save()
        return instance

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingridients = validated_data.pop('recipeingridient_set')
        instance.image = validated_data['image']
        instance.text = validated_data['text']
        instance.cooking_time = validated_data['cooking_time']
        instance.save()
        
        RecipeTag.objects.filter(recipe_id=instance).exclude(
            tag_id__in=tags).delete()
        for tag in tags:
            RecipeTag.objects.get_or_create(
                tag_id=tag,
                recipe_id=instance
            )

        RecipeIngridient.objects.filter(recipe_id=instance).delete()
        for i in ingridients:
            RecipeIngridient.objects.create(
                recipe_id=instance,
                ingridient_id=i['id'],
                amount=i['amount']
            )

        return instance


class NestedRecipeSerializer(RecipeSerializer):
    class Meta:
        model = Recipe
        fields = (
            'id',
            'image',
            'name',
            'cooking_time',
        )


class UserSubscribedSerializer(UserSerializer):
    recipes = NestedRecipeSerializer(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_recipes_count(self, obj):
        return obj.recipes.count()

class SubscriptionSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField(source='following.email')
    id = serializers.ReadOnlyField(source='following.id')
    first_name =serializers.ReadOnlyField(source='following.first_name')
    last_name = serializers.ReadOnlyField(source='following.last_name')
    username = serializers.ReadOnlyField(source='following.username')
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Subscription
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'recipes',
            'recipes_count'
        )
    def get_recipes(self, obj):
        queryset = Recipe.objects.filter(author=obj.following)
        return NestedRecipeSerializer(queryset, many=True).data[:3]

    def get_recipes_count(self, obj):
        return obj.following.recipes.count()



class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngridientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingridient
        fields = ('id', 'name', 'measurement_unit')
