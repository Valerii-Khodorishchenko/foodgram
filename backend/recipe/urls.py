from django.urls import path

from recipe.views import recipe_redirect


app_name = 'recipe'

urlpatterns = [
    path('<int:pk>/', recipe_redirect, name='recipe')
]
