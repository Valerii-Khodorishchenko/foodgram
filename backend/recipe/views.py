from django.shortcuts import get_object_or_404, redirect

from recipe.models import Recipe


def recipe_redirect(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    return redirect('api:recipes-detail', pk=recipe.pk)


def redirect_short_link(request, short_id):
    recipe = get_object_or_404(Recipe, id=short_id)
    return redirect('recipe:recipe', pk=recipe.id)
