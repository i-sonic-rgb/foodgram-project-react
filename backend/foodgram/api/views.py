from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import (filters, mixins, permissions, status, viewsets)
from rest_framework.decorators import action, api_view
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import (
    AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response

from .filters import RecipeFilter
from .models import Ingridient, Recipe, RecipeIngridient, RecipeTag, Tag
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    IngridientSerializer, NestedUserSerializer, RecipeSerializer,
    SubscriptionSerializer, TagSerializer
)
from users.models import Subscription, User


class ListRetrieveViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    pass


class ListViewSet(
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    pass


class TagViewSet(ListRetrieveViewSet):
    queryset = Tag.objects.all()
    permission_classes = (AllowAny, )
    lookup_field = 'id'
    pagination_class = LimitOffsetPagination
    serializer_class = TagSerializer


class SubscriptionListViewSet(ListRetrieveViewSet):
    queryset = Subscription.objects.all()
    permission_classes = (IsAuthenticated,)
    pagination_class = LimitOffsetPagination
    serializer_class = SubscriptionSerializer



@api_view(['DELETE', 'POST'])
@login_required
def user_subscribe(request, user_id):
    if request.method == 'DELETE':
        get_object_or_404(
            Subscription,
            user=request.user,
            following__id=user_id
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    author = get_object_or_404(User, id=user_id)
    if (
        request.user != author
        and not Subscription.objects.filter(
            user=request.user,
            following=author
        ).exists()
    ):
        Subscription.objects.create(user=request.user, following=author)
    serializer = NestedUserSerializer(instance=author,)
    serializer.context['request']=request
    return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly, )
    serializer_class = RecipeSerializer
    lookup_field = 'id'
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, )
    filterset_class = RecipeFilter
    search_fields = ('$text',)
    pagination_class = LimitOffsetPagination
    http_method_names = ['get', 'post', 'patch', 'delete']


class IngridientViewSet(ListRetrieveViewSet):
    queryset = Ingridient.objects.all()
    permission_classes = (AllowAny, )
    lookup_field = 'id'
    pagination_class = LimitOffsetPagination
    serializer_class = IngridientSerializer
