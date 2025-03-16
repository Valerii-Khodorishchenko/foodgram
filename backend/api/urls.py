from django.conf import settings
from django.conf.urls import url
from django.urls import include, path
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.routers import DefaultRouter

from api.views import (
    IngredientViewSet,
    UserViewSet,
    RecipeViewSet,
    TagViewSet,
    redoc_view
)


app_name = 'api'

router = DefaultRouter()
router.register('users', UserViewSet, basename='users')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
    path('docs/', redoc_view, name='redoc'),
]

schema_view = get_schema_view(
    openapi.Info(
        title='Foodgram API',
        default_version='1.0.0',
        description='''Документация для приложения Foodgram API.
        API для управления рецептами, ингредиентами, подписками и
         пользователями.
        ''',
        contact=openapi.Contact(email='Khodorishchenko.Valerii@yandex.ru'),
        license=openapi.License(name='BSD License'),
    ),
    public=True,
)

if settings.DEBUG:
    urlpatterns += [
        url(r'^swagger(?P<format>\.json|\.yaml)$',
            schema_view.without_ui(cache_timeout=0), name='schema-json'),
        url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0),
            name='schema-swagger-ui'),
        url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0),
            name='schema-redoc'),
    ]
