import os

from django.db import models
from foodgram.settings import CHARFIELD_MAX_LENGTH, MEDIA_ROOT
from users.models import User


def get_upload_path(instance, filename):
    '''Returns an upload path to image based on Recipe instance.'''
    return os.path.join(
        MEDIA_ROOT, "recipes/images/", f"{instance.name}-{filename}"
    )


class Ingredient(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=250)
    measurement_unit = models.CharField(max_length=250)

    class Meta:
        ordering = ('name',)


class Tag(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=CHARFIELD_MAX_LENGTH, unique=True)
    color = models.CharField(max_length=CHARFIELD_MAX_LENGTH, unique=True,)
    slug = models.SlugField(max_length=CHARFIELD_MAX_LENGTH, unique=True,)


class Recipe(models.Model):
    id = models.AutoField(primary_key=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    image = models.ImageField(
        upload_to=get_upload_path,
        null=True,
        default=None
    )
    name = models.CharField(max_length=CHARFIELD_MAX_LENGTH)
    text = models.TextField()
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient'
    )
    tags = models.ManyToManyField(Tag, through='RecipeTag')
    cooking_time = models.IntegerField()
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


class RecipeIngredient(models.Model):
    recipe_id = models.ForeignKey(
        Recipe,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    ingredient_id = models.ForeignKey(
        Ingredient,
        on_delete=models.SET_NULL,
        related_name='recipes',
        blank=True,
        null=True
    )
    amount = models.IntegerField(blank=True, null=True)


class RecipeTag(models.Model):
    recipe_id = models.ForeignKey(
        Recipe,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    tag_id = models.ForeignKey(
        Tag,
        on_delete=models.SET_NULL,
        related_name='recipes',
        blank=True,
        null=True
    )

    class Meta:
        ordering = ('tag_id',)
        constraints = [
            models.UniqueConstraint(
                name="recipe_tag_unique_relationships",
                fields=["recipe_id", "tag_id"],
            ),
        ]


class RecipeListeBaseModel(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='%(class)ss',
        verbose_name='Пользователь',
    )

    class Meta:
        abstract = True


class Favorite(RecipeListeBaseModel):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт',
    )


class ShoppingCart(RecipeListeBaseModel):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='in_shopping_cart',
        verbose_name='Рецепт',
    )
