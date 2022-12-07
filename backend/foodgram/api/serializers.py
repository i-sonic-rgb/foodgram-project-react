import base64

import webcolors
from django.core.files.base import ContentFile
from django.core.validators import MinValueValidator
from rest_framework import serializers

from users.models import Subscription
from users.serializers import UserSerializer

from .models import Ingredient, Recipe, RecipeIngredient, RecipeTag, Tag, User


class Hex2NameColor(serializers.Field):
    def to_representation(self, value):
        try:
            value = webcolors.hex_to_name(value)
        except ValueError:
            value = 'black'
        return value

    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Для этого цвета нет имени')
        return data


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='image.' + ext)

        return super().to_internal_value(data)


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    color = Hex2NameColor()

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class TagField(serializers.RelatedField):
    def to_representation(self, obj):
        return TagSerializer(obj).data

    def to_internal_value(self, data):
        try:
            tag = Tag.objects.get(id=data)
        except Exception:
            raise serializers.ValidationError('No such tag!')
        return tag


class RecipeIngidientSerializer(serializers.Serializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(), required=True,
        source='ingredient_id.id'
    )
    name = serializers.ReadOnlyField(source='ingredient_id.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient_id.measurement_unit'
    )
    amount = serializers.IntegerField(
        required=True, validators=[MinValueValidator(1), ]
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(many=False, read_only=True)
    image = Base64ImageField(required=False,)
    cooking_time = serializers.IntegerField(required=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    ingredients = RecipeIngidientSerializer(
        required=True, many=True, source='recipeingredient_set'
    )
    tags = TagField(queryset=Tag.objects.all(), many=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'author',
            'image',
            'name',
            'text',
            'ingredients',
            'cooking_time',
            'is_favorited',
            'is_in_shopping_cart',
            'tags'
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

    def validate_ingredients(self, value):
        if len(value) == 0:
            raise serializers.ValidationError(
                'at least one ingredient required!'
            )
        return value

    def create(self, validated_data):
        # only unique tags available.
        tags = set(validated_data.pop('tags'))
        ingredients = validated_data.pop('recipeingredient_set')
        instance = Recipe.objects.create(
            author=self.context['request'].user, **validated_data
        )

        for tag in tags:
            tag_instance = RecipeTag(tag_id=tag, recipe_id=instance)
            tag_instance.save()

        # If user add several identical ingridients, their amount sums.
        dataset = {}
        for ingredient in ingredients:
            if ingredient['ingredient_id']['id'] in dataset.keys():
                dataset[
                    ingredient['ingredient_id']['id']
                ] += ingredient['amount']
            else:
                dataset[
                    ingredient['ingredient_id']['id']
                ] = ingredient['amount']
        for id, amount in dataset.items():
            ri = RecipeIngredient(
                ingredient_id=id,
                recipe_id=instance,
                amount=amount
            )
            ri.save()
        instance.save()
        return instance

    def update(self, instance, validated_data):
        tags = set(validated_data.pop('tags'))
        ingredients = validated_data.pop('recipeingredient_set')
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data['text']
        instance.cooking_time = validated_data['cooking_time']
        instance.save()

        RecipeTag.objects.filter(recipe_id=instance).exclude(
            tag_id__in=tags
        ).delete()
        for tag in tags:
            RecipeTag.objects.get_or_create(tag_id=tag, recipe_id=instance)

        RecipeIngredient.objects.filter(recipe_id=instance).delete()

        # If user add several identical ingridients, their amount sums.
        dataset = {}
        for ingredient in ingredients:
            if ingredient['ingredient_id']['id'] in dataset.keys():
                dataset[
                    ingredient['ingredient_id']['id']
                ] += ingredient['amount']
            else:
                dataset[
                    ingredient['ingredient_id']['id']
                ] = ingredient['amount']
        for id, amount in dataset.items():
            RecipeIngredient.objects.create(
                recipe_id=instance,
                ingredient_id=id,
                amount=amount
            )

        return instance


class NestedRecipeSerializer(RecipeSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'image', 'name', 'cooking_time',)


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
    first_name = serializers.ReadOnlyField(source='following.first_name')
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
        return NestedRecipeSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return obj.following.recipes.count()
