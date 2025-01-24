from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from django.db.models import Count

from recipe.admin.mixins import DisplayImageMixin, ImagePreviewMixin
from recipe.constants import ITEMS_PER_PAGE
from recipe.models import User
from recipe.validators import validate_image_size


class UserForm(ImagePreviewMixin, UserChangeForm):
    class Meta:
        model = User
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['avatar'].required = False
        self.add_image_preview('avatar', self.instance)

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        validate_image_size(avatar)
        return avatar


class CustomUserAdmin(DisplayImageMixin, UserAdmin):
    form = UserForm
    list_display = (
        'username', 'display_avatar', 'email', 'first_name', 'last_name',
        'get_followers_count', 'get_favorites_count', 'get_cart_count'
    )
    fieldsets = (
        (None, {'fields': ('avatar',)}),
        ('Учётные данные пользователя', {'fields': (
            'first_name', 'last_name', 'username', 'email', 'password'
        )}),
        ('Разрешения', {'fields': (
            'is_active', 'is_staff', 'is_superuser',
        )}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'first_name', 'last_name', 'username', 'email', 'password1',
                'password2', 'is_superuser', 'is_staff', 'is_active'
            )}
         ),
    )
    filter_horizontal = ('followings', 'cart', 'favorites')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username', 'email')
    list_per_page = ITEMS_PER_PAGE

    def display_avatar(self, user):
        return self.display_image(user, 'avatar')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(
            followers_count=Count('followers'),
            favorites_count=Count('favorites'),
            cart_count=Count('cart'),
        )

    def get_followers_count(self, user):
        return user.followers_count

    def get_favorites_count(self, user):
        return user.favorites_count

    def get_cart_count(self, user):
        return user.cart_count

    get_followers_count.admin_order_field = 'followers_count'
    get_favorites_count.admin_order_field = 'favorites_count'
    get_cart_count.admin_order_field = 'cart_count'
    display_avatar.short_description = 'Аватарка'
    get_followers_count.short_description = 'Подписчики'
    get_favorites_count.short_description = 'Понравилось'
    get_cart_count.short_description = 'Корзина'
