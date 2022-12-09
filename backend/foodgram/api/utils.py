import io

from django.shortcuts import get_object_or_404
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import status
from rest_framework.response import Response

from .models import Recipe
from .serializers import NestedRecipeSerializer


def favorite_shoppingcart_func(request, model, recipe_id):
    '''Common function for favorite and shopping cart view functions.

    Recieve request, model - Favorite or ShoppingCart - and recipe id.
    '''
    if request.method == 'DELETE':
        get_object_or_404(
            model,
            user=request.user,
            recipe__id=recipe_id
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    recipe = get_object_or_404(Recipe, id=recipe_id)
    if not model.objects.filter(
            user=request.user,
            recipe__id=recipe_id
    ).exists():
        model.objects.create(user=request.user, recipe=recipe)
    serializer = NestedRecipeSerializer(instance=recipe)
    return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)


def pdf_from_shopping_cart(shopping_cart):
    sentence = ''
    for ingredient in shopping_cart:
        sentence += '{name} ({measurement_unit}) - {amount}\n'.format(
            name=ingredient['recipe__recipeingredient__ingredient__name'],
            measurement_unit=ingredient[
                'recipe__recipeingredient__ingredient__measurement_unit'
            ],
            amount=ingredient['count']
        )
    sentence += 'Thanks! Your shopping list is created by IP.'

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer)
    pdfmetrics.registerFont(TTFont('FreeSans', './FreeSans.ttf'))
    c.setFont('FreeSans', 12)
    textobject = c.beginText(2 * cm, 29.7 * cm - 2 * cm)
    for line in sentence.splitlines(False):
        textobject.textLine(line.encode('utf-8'))
    c.drawText(textobject)
    c.save()
    buffer.seek(0)
    return buffer
