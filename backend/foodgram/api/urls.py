from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (IngredientViewSet, RecipeViewSet, SubscriptionListViewSet,
                    TagViewSet, download_shopping_cart, recipe_favorite,
                    shopping_cart, user_subscribe)
from users.views import UserResetPasswordViewSet, UserViewSet

app_name = 'api'

v1_router = DefaultRouter()
v1_router.register(
    'users/subscriptions', SubscriptionListViewSet, basename='subscriptions'
)
v1_router.register(
    'users/set_password', UserResetPasswordViewSet, basename='reset_password'
)
v1_router.register('users', UserViewSet, basename='users')
v1_router.register('recipes', RecipeViewSet, basename='recipes')
v1_router.register('tags', TagViewSet, basename='tags')
v1_router.register('ingredients', IngredientViewSet, basename='ingredients')


urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('users/<int:user_id>/subscribe/', user_subscribe, name='subscribe'),
    path(
        'recipes/<int:recipe_id>/favorite/',
        recipe_favorite,
        name='recipe_favorite'
    ),
    path(
        'recipes/<int:recipe_id>/shopping_cart/',
        shopping_cart,
        name='shopping_cart'
    ),
    path(
        'recipes/download_shopping_cart/',
        download_shopping_cart,
        name='download_shopping_cart'
    ),
    path('', include(v1_router.urls)),
]
