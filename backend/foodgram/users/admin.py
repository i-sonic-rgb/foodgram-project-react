from django.contrib import admin

from .models import Subscription, User


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'username',
        'email',
        'role',
        'first_name',
        'last_name'
    )
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('role', )
    list_editable = ('role',)
    empty_value_display = '-пусто-'

class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'following',
    )
    search_fields = ('following', )
    list_filter = ('user', )
    empty_value_display = '-пусто-'


admin.site.register(User, UserAdmin)
admin.site.register(Subscription, SubscriptionAdmin)