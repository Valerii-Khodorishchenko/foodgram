from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.db.models import Count

from recipe.admin.filters import (
    HasFollowersFilter, HasRecipesFilter, HasSubscriptionsFilter)
from recipe.admin.mixins import DisplayImageMixin
from recipe.constants import ITEMS_PER_PAGE
from recipe.models import Cart, Favorites, Follow


class UserAdmin(DisplayImageMixin, UserAdmin):
    list_display = (
        'username', 'display_avatar', 'email', 'get_full_name',
        'followers_count', 'following_count', 'favorites_count', 'cart_count'
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
        return super().formfield_for_dbfield(
            db_field, model=get_user_model(), field_name='avatar', **kwargs)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(
            followings_count=Count('followers'),
            favorites_count=Count('favorites'),
            cart_count=Count('cart'),
        )

    @admin.display(description='Полное имя')
    def get_full_name(self, user):
        return f'{user.last_name} {user.first_name}'

    @admin.display(description='Понравилось')
    def favorites_count(self, obj):
        return obj.favorites.all().count()

    @admin.display(description='Корзина')
    def cart_count(self, user):
        return user.cart.all().count()

    @admin.display(description='Подписки')
    def followers_count(self, users):
        return users.followers.count()

    @admin.display(description='Подписчики')
    def following_count(self, users):
        return users.following.count()

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change, field_name='avatar')

    def delete_model(self, request, obj):
        super().delete_model(request, obj, field_name='avatar')

    def delete_queryset(self, request, queryset):
        super().delete_queryset(request, queryset, field_name='avatar')


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'following')
    search_fields = ('user__username', 'following__username')
    list_filter = ('user', 'following')
    ordering = ('user',)


@admin.register(Favorites)
class FavoritesAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe', 'created_at')
    search_fields = ('user__username', 'recipe__name')
    list_filter = ('user', 'recipe')
    ordering = ('-created_at',)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe', 'added_at')
    search_fields = ('user__username', 'recipe__name')
    list_filter = ('user', 'recipe')
    ordering = ('-added_at',)
