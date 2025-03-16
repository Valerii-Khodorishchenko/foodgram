from django.shortcuts import redirect
from django.http import Http404

from recipe.models import Recipe


def recipe_redirect(request, recipe_id):
    try:
        Recipe.objects.get(pk=recipe_id)
        return redirect(f'/api/recipes/{recipe_id}/')
    except Recipe.DoesNotExist:
        raise Http404('Ссылка не действительна')
