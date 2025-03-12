from django.apps import AppConfig
from django.contrib import admin
from django.contrib.admin import AdminSite


class RecipeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'recipe'
    verbose_name = 'Рецепты'


class AdminSite(AdminSite):
    site_header = 'Управление приложением FOODGRAM'
    site_title = 'FOODGRAM'
    index_title = 'Администрирование'

    def get_app_list(self, request):
        app_list = super().get_app_list(request)
        order = ['user', 'tag', 'recipe', 'ingredient']
        for app in app_list:
            if app['app_label'] == 'recipe':
                app['models'].sort(
                    key=lambda m: order.index(m['object_name'].lower())
                    if m['object_name'].lower() in order else 100
                )
        return app_list


admin.site = AdminSite()
