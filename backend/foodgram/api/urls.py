
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from users.views import (
    UserViewSet
)
from .views import RecipeViewSet, SubscriptionViewSet

app_name = 'api'

v1_router = DefaultRouter()
v1_router.register(
    'users/subscriptions', SubscriptionViewSet, basename='subscriptions'
)
v1_router.register('users', UserViewSet, basename='users')
v1_router.register('recipes', RecipeViewSet, basename='recipes')


urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(v1_router.urls)),
]
