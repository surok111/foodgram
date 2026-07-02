from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from django.http import Http404
from rest_framework.routers import DefaultRouter

from users.views import UserViewSet
from recipes.views import TagViewSet, IngredientViewSet, RecipeViewSet
from recipes.models import Recipe

router = DefaultRouter()
router.register('users', UserViewSet, basename='users')
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')


def redirect_short_link(request, short_link):
    try:
        recipe = Recipe.objects.get(short_link=short_link)
        return redirect(f'/recipes/{recipe.id}/')
    except Recipe.DoesNotExist:
        raise Http404


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('api/auth/', include('djoser.urls.authtoken')),
    path('s/<str:short_link>/', redirect_short_link, name='short-link'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
