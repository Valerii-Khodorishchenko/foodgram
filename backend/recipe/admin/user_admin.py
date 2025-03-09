from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.db.models import Count

from recipe.admin.filters import (
    HasFollowersFilter, HasRecipesFilter, HasSubscriptionsFilter)
from recipe.admin.mixins import DisplayImageMixin
from recipe.constants import ITEMS_PER_PAGE


class UserAdmin(DisplayImageMixin, UserAdmin):
    list_display = (
        'username', 'display_avatar', 'email', 'get_full_name',
        'get_followers_count', 'get_favorites_count', 'get_cart_count'
    )
    fieldsets = (
        (None, {'fields': ('avatar',)}),
        ('Учётные данные пользователя', {'fields': (
            'first_name', 'last_name', 'username', 'email', 'password'
        )}),
        ('Разрешения', {'fields': (
            'is_active', 'is_superuser',
        )}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'first_name', 'last_name', 'username', 'email', 'password1',
                'password2', 'is_superuser', 'is_active'
            )}
         ),
    )
    filter_horizontal = (
        # 'followings',
        'cart',
        'favorites'
    )
    search_fields = ('username', 'email', 'get_full_name')
    ordering = ('username', 'email')
    list_filter = (
        'is_superuser', 'is_active',
        HasRecipesFilter, HasFollowersFilter, HasSubscriptionsFilter
    )
    list_per_page = ITEMS_PER_PAGE

    @admin.display(description='Аватарка')
    def display_avatar(self, user):
        return self.display_image(user, 'avatar')
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        return super().formfield_for_dbfield(db_field, model=get_user_model(), field_name='avatar', **kwargs)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(
            followers_count=Count('followers'),
            favorites_count=Count('favorites'),
            cart_count=Count('cart'),
        )

    @admin.display(description='Полное имя')
    def get_full_name(self, user):
        return f'{user.last_name} {user.first_name}'

    @admin.display(description='Подписчики')
    def get_followers_count(self, user):
        return user.followers_count

    @admin.display(description='Понравилось')
    def get_favorites_count(self, user):
        return user.favorites_count

    @admin.display(description='Корзина')
    def get_cart_count(self, user):
        return user.cart_count

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change, field_name='avatar')

    def delete_model(self, request, obj):
        super().delete_model(request, obj, field_name='avatar')

    def delete_queryset(self, request, queryset):
        super().delete_queryset(request, queryset, field_name='avatar')
