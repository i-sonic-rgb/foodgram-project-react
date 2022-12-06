
import io


from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont 
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import  api_view
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from .filters import RecipeFilter
from .models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from .paginations import RecipePagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    IngredientSerializer, UserSubscribedSerializer, RecipeSerializer,
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
    serializer_class = TagSerializer


class SubscriptionListViewSet(ListViewSet):
    queryset = Subscription.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = SubscriptionSerializer
    pagination_class = RecipePagination


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
    ingredient_id и amount. С помощью annotate создаем новое значение count, 
    в котором суммируем значения всех amount для одинаковых ингридиентов.'''

    shopping_cart = request.user.shoppingcarts.all().values(
            'recipe__recipeingredient__ingredient_id__id',
            'recipe__recipeingredient__ingredient_id__name',
            'recipe__recipeingredient__ingredient_id__measurement_unit'
        ).order_by(
            'recipe__recipeingredient__ingredient_id__name'
        ).annotate(count=Sum('recipe__recipeingredient__amount'))
    if len(shopping_cart) < 1:
        return Response(
            'Your shopping list is empty!', status=status.HTTP_204_NO_CONTENT
        )
    sentence=''
    for ingredient in shopping_cart:
        sentence += '{name} ({measurement_unit}) - {amount}\n'.format(
            name=ingredient['recipe__recipeingredient__ingredient_id__name'],
            measurement_unit=ingredient[
                'recipe__recipeingredient__ingredient_id__measurement_unit'
            ],
            amount=ingredient['count']
        )
    sentence += 'Thanks! Your shopping list is created by IP.'
    
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer)
    pdfmetrics.registerFont(TTFont('FreeSans', './FreeSans.ttf'))
    c.setFont('FreeSans', 12)
    textobject = c.beginText(2*cm, 29.7 * cm - 2 * cm)
    for line in sentence.splitlines(False):
        textobject.textLine(line.encode('utf-8'))
    c.drawText(textobject)
    c.save()
    buffer.seek(0)

    response = FileResponse(buffer, as_attachment=True, filename='List.pdf')
    return response


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly, )
    serializer_class = RecipeSerializer
    lookup_field = 'id'
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, )
    pagination_class = RecipePagination
    filterset_class = RecipeFilter
    search_fields = ('$text',)
    http_method_names = ['get', 'post', 'patch', 'delete']


class IngredientViewSet(ListRetrieveViewSet):
    queryset = Ingredient.objects.all()
    permission_classes = (AllowAny, )
    lookup_field = 'id'
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,  filters.SearchFilter,)
    pagination_class = LimitOffsetPagination
    search_fields = ('$name',)



# @action(['post'], detail=False, name='Add recipe to favorite',
#             url_path=r'(?P<recipe_id>\d+)/favorite')
#     def favorite(self, request, *args, **kwargs):
#         return ...
# Если добавить detail=True, то автоматом будет id перед именем вставлен
