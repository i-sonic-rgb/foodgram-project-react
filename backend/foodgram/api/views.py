from django.shortcuts import get_object_or_404
from rest_framework import (filters, permissions, status, viewsets)
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Recipe
from .serializers import RecipeSerializer
from users.models import User

class SubscriptionViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    pagination_class = LimitOffsetPagination
    serializer_class = RecipeSerializer

    def get_queryset(self):
        return Recipe.objects.filter(author__following__user=self.request.user)

class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (AllowAny, )
    lookup_field = 'id'
    search_fields = ('author',)
    pagination_class = LimitOffsetPagination
    serializer_class = RecipeSerializer