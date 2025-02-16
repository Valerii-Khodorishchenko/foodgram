import os

from django.conf import settings
from django.contrib import admin
from django.db.models import Count
from django.utils.safestring import mark_safe

from recipe.constants import DISPLAY_IMAGE_SIZE, IMAGE_PREVIEW_SIZE


@mark_safe
def get_img(img_url, size, help_text=''):
    if help_text:
        help_text = f'<p>{help_text}</p>'
    return (
        f'<a href="{img_url}" target="_blank">'
        f'<img src="{img_url}" style="width: {size}px; '
        f'max-height: {size}px; object-fit: cover;" /></a>{help_text}'
    )


class DisplayImageMixin:
    from recipe.models import Recipe
    @admin.display(description='Изображение')
    def display_image(self, obj, image_field='image'):
        image = getattr(obj, image_field, None)
        if image and hasattr(image, 'url'):
            file_path = os.path.join(settings.MEDIA_ROOT, image.name)
            if os.path.exists(file_path):
                return get_img(image.url, DISPLAY_IMAGE_SIZE)
            return 'Неверный путь к файлу'
        return 'Отсутствует'

    def formfield_for_dbfield(self, db_field, model=Recipe, field_name='image', **kwargs):
        field = super().formfield_for_dbfield(db_field, **kwargs)
        if request := kwargs.get('request'):
            field.help_text = self.add_image_preview_to_field(db_field, request, model=model, field_name=field_name)
        return field

    def add_image_preview_to_field(self, db_field, request, model, field_name):
        if db_field.name == field_name:

            object_id = request.resolver_match.kwargs.get('object_id')
            if model_object := model.objects.filter(id=object_id).first():
                image = getattr(model_object, field_name, None)
                if image and hasattr(image, 'url'):
                    file_path = os.path.join(settings.MEDIA_ROOT, image.name)
                    if os.path.exists(file_path):
                        return get_img(image.url, DISPLAY_IMAGE_SIZE)

    def save_model(self, request, obj, form, change, field_name='image'):
        if change:
            old_instance = self.model.objects.get(pk=obj.pk)
            old_file = getattr(old_instance, field_name, None)
            if old_file and old_file != getattr(obj, field_name, None):
                old_file.delete(save=False)
        obj.save()

    def delete_model(self, request, obj, field_name='image'):
        if obj_file := getattr(obj, field_name, None):
            obj_file.delete(save=False)
        obj.delete()

    def delete_queryset(self, request, queryset, field_name='image'):
        for obj in queryset:
            self.delete_model(request, obj)


# class ImagePreviewMixin:
#     def add_image_preview(self, field_name, instance):
#         if (
#             (field := self.fields.get(field_name))
#             and (field_value := getattr(instance, field_name, None))
#             and instance.pk
#         ):
#             field.widget = forms.FileInput()
#             field.help_text = get_img(
#                 field_value.url, IMAGE_PREVIEW_SIZE, help_text=field.help_text)


class RecipesAdminMixin:
    list_display: tuple[str, ...] = ('get_recipes_count',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(
            recipes_count=Count('recipes')
        ).prefetch_related('recipes')

    @admin.display(description='Рецептов')
    def get_recipes_count(self, obj):
        return obj.recipes_count
