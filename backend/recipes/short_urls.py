from django.urls import path
from django.shortcuts import get_object_or_404, redirect
from recipes.models import Recipe


def short_link_redirect(request, short_id):
    recipe = get_object_or_404(Recipe, short_id=short_id)
    return redirect(f'/recipes/{recipe.pk}')


urlpatterns = [
    path('<str:short_id>', short_link_redirect, name='short-link'),
]
