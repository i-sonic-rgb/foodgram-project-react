from django.db import models

from foodgram.settings import CHARFIELD_MAX_LENGTH
from users.models import User


class Ingridient(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=250)
    measurement_unit = models.CharField(max_length=250)


class Tag(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=CHARFIELD_MAX_LENGTH)
    color = models.CharField(max_length=CHARFIELD_MAX_LENGTH)
    slug = models.SlugField(max_length=CHARFIELD_MAX_LENGTH)


class Recipe(models.Model):
    id = models.AutoField(primary_key=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    image = models.TextField(blank=True, null=True)
    name = models.CharField(max_length=250)
    text = models.TextField(blank=True, null=True)
    ingridients = models.ManyToManyField(
        Ingridient,
        through='RecipeIngridient'
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


class RecipeIngridient(models.Model):
    recipe_id = models.ForeignKey(
        Recipe,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    ingridient_id = models.ForeignKey(
        Ingridient,
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

