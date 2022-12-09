import os

from django.core.validators import MinValueValidator
from django.db import models

from foodgram.settings import (CHARFIELD_MAX_LENGTH, MEDIA_ROOT,
                               NAMES_MAX_LENGTH)
from users.models import User


def get_upload_path(instance, filename):
    '''Returns an upload path to image based on Recipe instance name.'''
    return os.path.join(
       "recipes/images/", f"{instance.name}-{filename}"
    )


class Ingredient(models.Model):
    '''Model for Ingridient objects.'''
    name = models.CharField(
        max_length=NAMES_MAX_LENGTH,
        verbose_name='Наименование ингредиента',
        unique=True,
        blank=False,
        null=False,
    )
    measurement_unit = models.CharField(
        max_length=NAMES_MAX_LENGTH,
        verbose_name='Единица измерений',
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self) -> str:
        return self.name


class Tag(models.Model):
    '''Model for Tag objects.'''
    name = models.CharField(
        max_length=CHARFIELD_MAX_LENGTH,
        verbose_name='Наименование тэга',
        unique=True,
        blank=False,
        null=False,
    )
    color = models.CharField(
        max_length=CHARFIELD_MAX_LENGTH,
        verbose_name='Цвет тэга',
        unique=True,
        blank=False,
        null=False,
    )
    slug = models.SlugField(
        max_length=CHARFIELD_MAX_LENGTH,
        verbose_name='Идентификатор тэга',
        unique=True,
        blank=False,
        null=False,
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ('name',)

    def __str__(self) -> str:
        return self.name


class Recipe(models.Model):
    '''Model for Recipe objects. Tags and ingridients are many-to-many.'''
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    image = models.ImageField(
        upload_to=get_upload_path,
        null=False,
        blank=False,
        verbose_name='Изображение'
    )
    name = models.CharField(
        max_length=CHARFIELD_MAX_LENGTH,
        verbose_name='Наименование рецепта',
        null=False,
        blank=False
    )
    text = models.TextField(verbose_name='Текст', blank=False, null=False,)
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингредиенты',
        blank=False
    )
    tags = models.ManyToManyField(
        Tag, through='RecipeTag', verbose_name='Тэги', blank=False
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления',
        validators=[MinValueValidator(1), ],
        null=False,
        blank=False
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self) -> str:
        return self.name


class RecipeIngredient(models.Model):
    '''Custom M2M model for Recipe and Ingridient tables connection.'''
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.SET_NULL,
        related_name='recipes',
        blank=True,
        null=True,
        verbose_name='Ингредиент'
    )
    amount = models.PositiveIntegerField(
        validators=[MinValueValidator(1), ],
        verbose_name='Количество'
    )

    class Meta:
        ordering = ('recipe',)
        verbose_name = 'Ингредиенты в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'
        constraints = [
            models.UniqueConstraint(
                name="recipe_ingredient_unique_relationships",
                fields=["recipe", "ingredient"],
            ),
        ]


class RecipeTag(models.Model):
    '''Custom M2M model for Recipe and Tag tables connection.'''
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='Рецепт'
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.SET_NULL,
        related_name='recipes',
        blank=True,
        null=True,
        verbose_name='Тэг'
    )

    class Meta:
        ordering = ('tag',)
        constraints = [
            models.UniqueConstraint(
                name="recipe_tag_unique_relationships",
                fields=["recipe", "tag"],
            ),
        ]


class RecipeListeBaseModel(models.Model):
    '''Parent abstract class for Favorite and ShoppingCart models.'''
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='%(class)ss',
        verbose_name='Пользователь',
    )

    class Meta:
        abstract = True


class Favorite(RecipeListeBaseModel):
    '''Model for adding recipes to favorite.'''
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепт'
        constraints = [
            models.UniqueConstraint(
                name="favorite_unique_relationships",
                fields=["user", "recipe"],
            ),
        ]


class ShoppingCart(RecipeListeBaseModel):
    '''Model for adding recipes to shopping cart.'''
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='in_shopping_cart',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Рецепт в корзине'
        verbose_name_plural = 'Рецепты в корзине'
        constraints = [
            models.UniqueConstraint(
                name="shopping_cart_unique_relationships",
                fields=["user", "recipe"],
            ),
        ]
