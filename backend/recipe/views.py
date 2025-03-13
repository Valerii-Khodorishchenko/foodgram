from django.shortcuts import redirect
from rest_framework import status
from rest_framework.response import Response

from recipe.models import Recipe


def recipe_redirect(request, recipe_id):
    if Recipe.objects.filter(pk=recipe_id).exists():
        return redirect('api:recipes-detail', pk=recipe_id)
    return Response(status=status.HTTP_404_NOT_FOUND)
