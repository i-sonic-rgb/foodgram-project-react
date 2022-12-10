from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import api_view
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .filters import IngredientSearchFilter, RecipeFilter
from .mixins import ListRetrieveViewSet, ListViewSet
from .models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from .paginations import RecipePagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (IngredientSerializer, RecipeSerializer,
                          SubscriptionSerializer, TagSerializer,
                          UserSubscribedSerializer)
from .utils import favorite_shoppingcart_func, pdf_from_shopping_cart
from users.models import Subscription, User


class TagViewSet(ListRetrieveViewSet):
    '''ViewSet for Tag model. Only GET requests. Return list or instance.'''
    queryset = Tag.objects.all()
    permission_classes = (AllowAny, )
    lookup_field = 'id'
    serializer_class = TagSerializer


class SubscriptionListViewSet(ListViewSet):
    '''ViewSet for Subscription model. Only GET requests. Return list.'''
    queryset = Subscription.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = SubscriptionSerializer
    pagination_class = RecipePagination


@api_view(['DELETE', 'POST'])
@login_required
def user_subscribe(request, user_id):
    '''ViewSet to supscripe (POST) and unsubscribed (DELETE) to author.'''
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
    serializer.context['request'] = request
    return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)


@api_view(['DELETE', 'POST'])
@login_required
def recipe_favorite(request, recipe_id):
    '''View function to add recipe to favorites.'''
    return favorite_shoppingcart_func(request, Favorite, recipe_id)


@api_view(['DELETE', 'POST'])
@login_required
def shopping_cart(request, recipe_id):
    '''Function to add recipes to of remove from  shopping cart.'''
    return favorite_shoppingcart_func(request, ShoppingCart, recipe_id)


@api_view(['GET'])
@login_required
def download_shopping_cart(request):
    '''Получаем данные из рецептов в корзине.

    Через related_name обращаемся к модели ShoppingCart, в ней - находим
    ingredient и amount. С помощью annotate создаем новое значение count,
    в котором суммируем значения всех amount для одинаковых ингридиентов.
    '''

    if not request.user.shoppingcarts.exists():
        return Response(
            'Your shopping list is empty!', status=status.HTTP_204_NO_CONTENT
        )

    shopping_cart = request.user.shoppingcarts.all().values(
        'recipe__recipeingredient__ingredient__id',
        'recipe__recipeingredient__ingredient__name',
        'recipe__recipeingredient__ingredient__measurement_unit'
    ).order_by(
        'recipe__recipeingredient__ingredient__name'
    ).annotate(count=Sum('recipe__recipeingredient__amount'))

    return FileResponse(
        pdf_from_shopping_cart(shopping_cart),
        as_attachment=True,
        filename='List.pdf'
    )


class RecipeViewSet(viewsets.ModelViewSet):
    '''ViewSet for Recipe model objects.'''
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly, )
    serializer_class = RecipeSerializer
    lookup_field = 'id'
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, )
    pagination_class = RecipePagination
    filterset_class = RecipeFilter
    search_fields = ('tags__name',)
    http_method_names = ['get', 'post', 'patch', 'delete']


class IngredientViewSet(ListRetrieveViewSet):
    '''ViewSet for Ingredient model objects.'''
    queryset = Ingredient.objects.all()
    permission_classes = (AllowAny, )
    lookup_field = 'id'
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend, )
    filterset_class = IngredientSearchFilter
    pagination_class = LimitOffsetPagination
