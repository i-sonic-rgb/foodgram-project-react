import os

from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import (filters, mixins, permissions, status, viewsets)
from rest_framework.decorators import action, api_view
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import (
    AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response

from foodgram.settings import MEDIA_ROOT
from .filters import RecipeFilter
from .models import (Favorite, Ingridient, Recipe, RecipeIngridient, RecipeTag,
                     ShoppingCart, Tag
                    )
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    IngridientSerializer, UserSubscribedSerializer, RecipeSerializer,
    SubscriptionSerializer, TagSerializer, NestedRecipeSerializer
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


class SubscriptionListViewSet(ListViewSet):
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
    serializer = UserSubscribedSerializer(instance=author,)
    serializer.context['request']=request
    return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)


@api_view(['DELETE', 'POST'])
@login_required
def recipe_favorite(request, recipe_id):
    '''Функция для добавления и удаления рецептов в избранное.'''
    if request.method == 'DELETE':
        get_object_or_404(
            Favorite,
            user=request.user,
            recipe__id=recipe_id
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    recipe = get_object_or_404(Recipe, id=recipe_id)
    if not Favorite.objects.filter(
            user=request.user,
            recipe__id=recipe_id
        ).exists():
        Favorite.objects.create(user=request.user, recipe=recipe)
    serializer = NestedRecipeSerializer(instance=recipe)
    return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)


@api_view(['DELETE', 'POST'])
@login_required
def shopping_cart(request, recipe_id):
    '''Функция для добавления и удаления рецептов в корзину рецептов.'''

    if request.method == 'DELETE':
        get_object_or_404(
            ShoppingCart,
            user=request.user,
            recipe__id=recipe_id
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    recipe = get_object_or_404(Recipe, id=recipe_id)
    if not ShoppingCart.objects.filter(
            user=request.user,
            recipe__id=recipe_id
        ).exists():
        ShoppingCart.objects.create(user=request.user, recipe=recipe)
    serializer = NestedRecipeSerializer(instance=recipe)
    return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@login_required
def download_shopping_cart(request):
    '''Получаем данные из рецептов в корзине. 
    
    Через related_name обращаемся к модели ShoppingCart, в ней - находим
    ingridient_id и amount. С помощью annotate создаем новое значение count, 
    в котором суммируем значения всех amount для одинаковых ингридиентов.'''

    shopping_cart = request.user.shoppingcarts.all().values(
            'recipe__recipeingridient__ingridient_id__id',
            'recipe__recipeingridient__ingridient_id__name',
            'recipe__recipeingridient__ingridient_id__measurement_unit'
        ).order_by(
            'recipe__recipeingridient__ingridient_id__name'
        ).annotate(count=Sum('recipe__recipeingridient__amount'))
    if len(shopping_cart) < 1:
        return Response(
            'Your shopping list is empty!', status=status.HTTP_204_NO_CONTENT
        )
    sentence=''
    for ingridient in shopping_cart:
        sentence += '{name} ({measurement_unit}) - {amount}\n'.format(
            name=ingridient['recipe__recipeingridient__ingridient_id__name'],
            measurement_unit=ingridient[
                'recipe__recipeingridient__ingridient_id__measurement_unit'
            ],
            amount=ingridient['count']
        )
    sentence += 'Thanks! Your shopping list is created by IP.'
    
    # Поскольку изначально директоря для media отсутствует, создаем ее.
    os.makedirs(os.path.dirname(f'{MEDIA_ROOT}/'), exist_ok=True)
    
    with open(
        f"{MEDIA_ROOT}/{request.user.username}-shoppinglsit.txt",
        "w", encoding="utf-8"
    ) as file:
        file.write(sentence)
    FileData = open(
        f"{MEDIA_ROOT}/{request.user.username}-shoppinglsit.txt",
        "r", encoding="utf-8"
    )
    response = HttpResponse(FileData, content_type='application/txt')
    response['Content-Disposition'] = 'attachment; filename=NameOfFile'
    os.remove(f"{MEDIA_ROOT}/{request.user.username}-shoppinglsit.txt")
    return response


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
    filter_backends = (filters.SearchFilter, )
    search_fields = ('$name',)


# @action(['post'], detail=False, name='Add recipe to favorite',
#             url_path=r'(?P<recipe_id>\d+)/favorite')
#     def favorite(self, request, *args, **kwargs):
#         return ...
# Если добавить detail=True, то автоматом будет id перед именем вставлен
