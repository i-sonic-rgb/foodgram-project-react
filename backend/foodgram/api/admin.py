from django.contrib import admin

from .models import (Favorite,  Ingridient, Recipe,RecipeIngridient, RecipeTag,
                     ShoppingCart, Tag)


class RecipeTagInline(admin.TabularInline):
    model = RecipeTag
    extra = 1


class RecipeIngridientInline(admin.TabularInline):
    model = RecipeIngridient
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'author',
        'text',
        'cooking_time',
        'get_tags'
    )
    inlines = (RecipeIngridientInline, RecipeTagInline)
    search_fields = ('text', 'author')
    list_filter = ('author',)
    empty_value_display = '-пусто-'
    def get_tags(self, obj):
        return [tag.name for tag in obj.tags.all()]


class IngridientAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'measurement_unit'
    )
    search_fields = ('name',)
    list_filter = ('measurement_unit',)
    empty_value_display = '-пусто-'


class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', 'slug')
    inlines = (RecipeTagInline,)
    search_fields = ('name', )
    empty_value_display = '-пусто-'


class FaworiteShoppingCartBase(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe',
    )
    search_fields = ('recipe', )
    list_filter = ('user', )
    empty_value_display = '-пусто-'


class FaworiteAdmin(FaworiteShoppingCartBase):
    pass


class ShoppingCartAdmin(FaworiteShoppingCartBase):
    pass


admin.site.register(Favorite, FaworiteAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.register(Ingridient, IngridientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)
