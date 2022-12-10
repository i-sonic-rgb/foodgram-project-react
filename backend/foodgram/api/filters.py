import django_filters
from django.db.models import Q, Value
from django.db.models.functions import StrIndex

from .models import Ingredient, Recipe


class RecipeFilter(django_filters.FilterSet):
    '''Custom filter for Recipes.'''
    is_favorited = django_filters.rest_framework.BooleanFilter(
        method='get_is_favorited'
    )
    is_in_shopping_cart = django_filters.rest_framework.BooleanFilter(
        method='get_is_in_shopping_cart'
    )
    tags = django_filters.rest_framework.CharFilter(method="get_tags")

    class Meta:
        model = Recipe
        fields = [
            'author',
            'tags',
            'is_favorited',
            'is_in_shopping_cart'
        ]

    def get_tags(self, queryset, name, value):
        '''Filter recipe's tags by Tag instance names.'''
        if value:
            return queryset.filter(
                tags__slug__in=set(dict(self.request.query_params)['tags'])
            ).distinct()
        return queryset

    def get_is_favorited(self, queryset, name, value):
        '''Return recipes which added to favorite by user. Filter by bool.'''
        if value:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        '''Return recipes added to shopping cart by user. Filter by bool.'''
        if value:
            return queryset.filter(in_shopping_cart__user=self.request.user)

        return queryset


class IngredientSearchFilter(django_filters.FilterSet):
    '''Custom search filter for Ingredients objects. Searh by name.'''
    name = django_filters.rest_framework.CharFilter(method='get_name')

    class Meta:
        model = Ingredient
        fields = [
            'name'
        ]

    def get_name(self, queryset, name, value):
        '''Return ingredients which name starts with value OR contains value.

        Case insensitive. Ingredients, which names STARTS WITHthe value,
        comes first.
        '''
        if value:
            return queryset.filter(
                Q(name__startswith=value.lower())
                | Q(name__icontains=value.lower())
            ).distinct().annotate(
                match=StrIndex('name', Value(value))
            ).order_by('match')
        return queryset
