from django.contrib import admin

from .models import (Favorite, ShoppingCart, Ingridient, Tag, Recipe,
                     RecipeIngridient, RecipeTag)


admin.site.register(Favorite)
admin.site.register(ShoppingCart)
admin.site.register(Ingridient)
admin.site.register(Tag)
admin.site.register(Recipe)
admin.site.register(RecipeIngridient)
admin.site.register(RecipeTag)