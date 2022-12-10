import django_filters

from .models import Ingredient, Recipe


class RecipeFilter(django_filters.FilterSet):
    '''Custom filter for Recipes.'''
    is_favorited = django_filters.rest_framework.BooleanFilter(
        method='get_is_favorited'
    )
    is_in_shopping_cart = django_filters.rest_framework.BooleanFilter(
        method='get_is_in_shopping_cart'
    )
    tags = django_filters.rest_framework.CharFilter(method='get_tags')

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
            return queryset.filter(tags__slug=value)
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
    name = django_filters.rest_framework.CharFilter(method='get_name')

    class Meta:
        model = Ingredient
        fields = [
            'name'
        ]

    def get_name(self, queryset, name, value):
        if value:
            return queryset.filter(name__startswith=value.lower())
        return queryset
