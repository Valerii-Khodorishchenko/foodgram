import re

from django.utils.text import slugify

from recipe.models import Tag
from recipe.management.base_import import BaseImport


class Command(BaseImport):
    help = 'Загружает теги в БД из CSV или JSON файла'
    model = Tag
    unique_fields = ('name',)

    def create(self, data):
        for tag in data:
            slug = tag['slug'] = tag.get('slug') or slugify(tag['name'])
            if not re.match(r'^[a-z0-9-]+$', slug):
                self.stdout.write(self.style.ERROR(
                    f'Неверный формат слага: {slug}'
                ))
                continue
            existing_tag = self.model.objects.filter(slug=slug)
            if (
                existing_tag.filter(name=tag['name']).exists()
                or not existing_tag.exists()
            ):
                super().create([tag])
            else:
                self.stdout.write(self.style.ERROR(
                    f'Slug {slug} уже занят тегом'
                    f' "{existing_tag.first().name}"!'
                ))
