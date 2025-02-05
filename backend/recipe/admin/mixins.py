import os

from django import forms
from django.db.models import Count
from django.utils.html import format_html
from django.conf import settings

from recipe.constants import (
    DISPLAY_IMAGE_SIZE,
    IMAGE_PREVIEW_SIZE,
    MAX_RECIPES
)


def get_img(img_url, size, help_text=''):
    if help_text:
        help_text = f'<p>{help_text}</p>'
    return format_html(
        f'<a href="{img_url}" target="_blank">'
        f'<img src="{img_url}" style="width: {size}px; '
        f'max-height: {size}px; object-fit: cover;" /></a>{help_text}'
    )


class DisplayImageMixin:
    def display_image(self, obj, image_field='image'):
        image = getattr(obj, image_field, None)
        if image and hasattr(image, 'url'):
            file_path = os.path.join(settings.MEDIA_ROOT, image.name)
            if os.path.exists(file_path):
                return get_img(image.url, DISPLAY_IMAGE_SIZE)
            return 'Неверный путь к файлу'
        return 'Отсутствует'

    def save_model(self, request, obj, form, change, field_name='image'):
        if change:
            old_instance = self.model.objects.get(pk=obj.pk)
            if (
                old_file := getattr(old_instance, field_name, None)
                != getattr(obj, field_name, None)
            ):
                old_file.delete(save=False)
        obj.save()

    def delete_model(self, request, obj, field_name='image'):
        if obj_file := getattr(obj, field_name, None):
            obj_file.delete(save=False)
        obj.delete()

    def delete_queryset(self, request, queryset, field_name='image'):
        for obj in queryset:
            self.delete_model(request, obj, field_name=field_name)

    display_image.short_description = 'Изображение'


class ImagePreviewMixin:
    def add_image_preview(self, field_name, instance):
        if (
            (field := self.fields.get(field_name))
            and (field_value := getattr(instance, field_name, None))
            and instance.pk
        ):
            field.widget = forms.FileInput()
            field.help_text = get_img(
                field_value.url, IMAGE_PREVIEW_SIZE, help_text=field.help_text)


class RecipesAdminMixin:
    list_display: tuple[str, ...] = ('get_recipes', 'get_recipes_count')
    ordering = ('name',)

    def get_recipes(self, obj):
        return format_html(
            ', '.join(
                [
                    f'<a href="/admin/recipe/recipe/{recipe.id}/">'
                    f'{recipe.name}</a>'
                    for recipe in obj.recipes.all()[:MAX_RECIPES]
                ]
            ) + ('...' if obj.recipes.count() > MAX_RECIPES else '')
        )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(
            recipes_count=Count('recipes')
        ).prefetch_related('recipes')

    def get_recipes_count(self, obj):
        return obj.recipes_count

    get_recipes_count.admin_order_field = 'recipes_count'
    get_recipes_count.short_description = 'Количество рецептов'
    get_recipes.short_description = 'Рецепты'
