from django.core.validators import MinValueValidator
from rest_framework import serializers

from .fields import Base64ImageField, Hex2NameColor
from .models import Ingredient, Recipe, RecipeIngredient, RecipeTag, Tag, User
from users.models import Subscription
from users.serializers import UserSerializer


class IngredientSerializer(serializers.ModelSerializer):
    '''Serializer for Ingredient nodel objects.'''
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    '''Serializer for Tag nodel objects.

    Color saved as HEX code and returns as name through custom field.
    '''
    color = Hex2NameColor()

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class RecipeIngidientSerializer(serializers.Serializer):
    '''Serializer for RecipeIngredient many-to-many objects.'''
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(), required=True,
        source='ingredient.id'
    )
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )
    amount = serializers.IntegerField(
        required=True, validators=[MinValueValidator(1), ]
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    '''Serializer for RecipeViewSet.'''
    author = UserSerializer(many=False, read_only=True)
    image = Base64ImageField(required=False,)
    cooking_time = serializers.IntegerField(required=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    ingredients = RecipeIngidientSerializer(
        required=True, many=True, source='recipeingredient_set'
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )

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
        '''Return True if recipe is in request user's favorite.'''
        if (
            'request' in self.context
            and self.context['request'].user.is_authenticated
        ):
            return obj in Recipe.objects.filter(
                favorites__user=self.context['request'].user
            )
        return False

    def get_is_in_shopping_cart(self, obj):
        '''Return True if recipe is in request user's shopping cart.'''
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
            raise serializers.ValidationError('At least one tag required!')
        return value

    def validate_ingredients(self, value):
        if len(value) == 0:
            raise serializers.ValidationError(
                'At least one ingredient required!'
            )
        dataset = {}
        for ingredient in value:
            if ingredient['ingredient']['id'] in dataset.keys():
                raise serializers.ValidationError(
                    "Several identical ingredients!"
                )
            dataset[
                ingredient['ingredient']['id']
            ] = ingredient['amount']
        return value

    def recipe_tags_ingredients(self, dataset, instance, tags):
        '''Function to create RecipeIngredient models while create/update.'''
        RecipeIngredient.objects.bulk_create([
            RecipeIngredient(
                ingredient=ingredient, recipe=instance, amount=amount
            ) for ingredient, amount in dataset.items()
        ])

        RecipeTag.objects.bulk_create([
            RecipeTag(tag=tag, recipe=instance) for tag in tags
        ])

    def create(self, validated_data):
        # only unique tags available.
        tags = set(validated_data.pop('tags'))
        ingredients = validated_data.pop('recipeingredient_set')
        dataset = {}
        for ingredient in ingredients:
            dataset[
                ingredient['ingredient']['id']
            ] = ingredient['amount']
        instance = Recipe.objects.create(
            author=self.context['request'].user, **validated_data
        )
        self.recipe_tags_ingredients(dataset, instance, tags)
        instance.save()
        return instance

    def update(self, instance, validated_data):
        tags = set(validated_data.pop('tags'))
        ingredients = validated_data.pop('recipeingredient_set')
        dataset = {}
        for ingredient in ingredients:
            dataset[
                ingredient['ingredient']['id']
            ] = ingredient['amount']
        RecipeIngredient.objects.filter(recipe=instance).delete()
        RecipeTag.objects.filter(recipe=instance).delete()
        self.recipe_tags_ingredients(dataset, instance, tags)

        super().update(instance, validated_data)
        return instance

    def to_representation(self, instance):
        '''Need this for tags field only.

        When creating/updating, provide list of int (as Tag pk). When
        retrieving object(s) - returns TagSerializer.
        '''
        representation = super(
            RecipeSerializer, self
        ).to_representation(instance)
        representation['tags'] = [
            {**TagSerializer(tag).data} for tag in instance.tags.all()
        ]
        return representation


class NestedRecipeSerializer(RecipeSerializer):
    '''Shortened RecipeSerializer (limited fields as required by redoc).'''
    class Meta:
        model = Recipe
        fields = ('id', 'image', 'name', 'cooking_time',)


class UserSubscribedSerializer(UserSerializer):
    '''Special serializer for author - returns after subscription thereon.

    Provides author's data together with his/her recipes and total number of
    his/her recipes.
    '''
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
        '''Return total number of author's recipes.'''
        return obj.recipes.count()


class SubscriptionSerializer(serializers.ModelSerializer):
    '''Serializer for Subscription page.

    Return author UserSerializer with his/her Recipes and total No of
    author's recipes.
    '''
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
        '''Return recipes serializers, total number is limited.'''
        limit = 3
        try:
            limit = self.context['request'].query_params.get('recipes_limit')
        except Exception:
            limit = 3
        return NestedRecipeSerializer(
            obj.following.recipes.all()[:limit], many=True
        ).data

    def get_recipes_count(self, obj):
        return obj.following.recipes.count()
