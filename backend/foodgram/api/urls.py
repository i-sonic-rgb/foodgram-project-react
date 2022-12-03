
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from users.views import (
    UserViewSet, UserResetPasswordViewSet
)
from .views import (
    IngridientViewSet, RecipeViewSet, SubscriptionListViewSet, TagViewSet, 
    user_subscribe, 
)

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
v1_router.register('ingridients', IngridientViewSet, basename='ingridients')


urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('users/<int:user_id>/subscribe/', user_subscribe, name='subscribe'),
    path('', include(v1_router.urls)),
]
