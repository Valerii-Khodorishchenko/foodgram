from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (
    IngredientViewSet,
    LoginView,
    logout,
    UserViewSet,
    RecipeViewSet,
    TagViewSet,
    redirect_short_link
)

router_v1 = DefaultRouter()
router_v1.register('users', UserViewSet, basename='users')
router_v1.register('recipes', RecipeViewSet, basename='recipes')
router_v1.register('tags', TagViewSet, basename='tags')
router_v1.register('ingredients', IngredientViewSet, basename='ingredients')

auth_patterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', logout, name='logout'),
]

urlpatterns = [
    path('s/<str:short_id>/', redirect_short_link, name='recipe-short-url'),
    path('auth/token/', include(auth_patterns)),
    path('', include(router_v1.urls)),
]
