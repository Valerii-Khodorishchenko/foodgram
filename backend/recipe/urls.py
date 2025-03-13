from django.urls import path

from recipe.views import recipe_redirect


app_name = 'recipe'

urlpatterns = [
    path('s/<str:recipe_id>/', recipe_redirect, name='recipe-short-url')
]
