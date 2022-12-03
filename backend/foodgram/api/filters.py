from django_filters import rest_framework as filters
import django_filters

from .models import Recipe

class RecipeFilter(django_filters.FilterSet):
    is_favorited = filters.BooleanFilter(method='get_is_favorited')
    is_in_shopping_cart=filters.BooleanFilter(method='get_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = [
            'author',
            'tags',
            'is_favorited',
            'is_in_shopping_cart'
        ]

    def get_is_favorited(self, queryset, name, value):
        if value:
            return queryset.filter(favorites__user=self.request.user)
        return queryset
    
    def get_is_in_shopping_cart(self, queryset, name, value):
        if value:
            return queryset.filter(in_shopping_cart__user=self.request.user)
        return queryset