from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import get_object_or_404, redirect
from django.urls import path, include

from recipes.models import Recipe


def redirect_short_link(request, short_link):
    recipe = get_object_or_404(Recipe, short_link=short_link)
    return redirect('recipes-detail', pk=recipe.id)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('api/auth/', include('djoser.urls.authtoken')),
    path('s/<str:short_link>/', redirect_short_link, name='short-url'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
