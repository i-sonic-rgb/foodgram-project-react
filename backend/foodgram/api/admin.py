from django.contrib import admin

from .models import (Favorite, Ingredient, Recipe, RecipeIngredient, RecipeTag,
                     ShoppingCart, Tag)


class RecipeTagInline(admin.TabularInline):
    '''Class for RecipeAdmin inline for RecipeTag M2M relations.'''
    model = RecipeTag
    extra = 1


class RecipeIngredientInline(admin.TabularInline):
    '''Class for RecipeAdmin inline for RecipeIngredient M2M relations.'''
    model = RecipeIngredient
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    '''Recipe AdminModel for standart DjangoAdmin panel.'''
    list_display = (
        'id',
        'author',
        'text',
        'get_tags',
        'name',
        'favorited',
    )
    inlines = (RecipeIngredientInline, RecipeTagInline)
    search_fields = ('text', 'author__username', 'name', )
    list_filter = ('author', 'name', 'tags')
    empty_value_display = '-пусто-'

    def get_tags(self, obj):
        '''Return tags of the Recipe names.'''
        return list(obj.tags.values_list('name', flat=True))

    def favorited(self, obj):
        return obj.favorites.count()


class IngredientAdmin(admin.ModelAdmin):
    '''Ingredient AdminModel for standart DjangoAdmin panel.'''
    list_display = (
        'id',
        'name',
        'measurement_unit'
    )
    search_fields = ('name',)
    list_filter = ('name',)


class TagAdmin(admin.ModelAdmin):
    '''Admin for tags. Slug field created automatically (can be changed).'''
    list_display = ('id', 'name', 'color', 'slug')
    inlines = (RecipeTagInline,)
    search_fields = ('name', )
    prepopulated_fields = {'slug': ('name',)}


class FaworiteShoppingCartBase(admin.ModelAdmin):
    '''Common base AdminModel for Favorite and ShoppingCart classes.'''
    list_display = (
        'user',
        'recipe',
    )
    search_fields = ('recipe', )
    list_filter = ('user', )
    empty_value_display = '-пусто-'


class FaworiteAdmin(FaworiteShoppingCartBase):
    '''Favorite AdminModel for standart DjangoAdmin panel.'''
    pass


class ShoppingCartAdmin(FaworiteShoppingCartBase):
    '''ShoppingCart AdminModel for standart DjangoAdmin panel.'''
    pass


class RecipeIngredientAdmin(admin.ModelAdmin):
    '''AdminModel for standart Django panel for RecipeTag M2M model.'''
    list_display = ('id', 'ingredient', 'recipe', 'amount')


admin.site.register(Favorite, FaworiteAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(RecipeIngredient, RecipeIngredientAdmin)
