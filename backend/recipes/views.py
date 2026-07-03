from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.urls import reverse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .filters import IngredientFilter, RecipeFilter
from .models import (
    Favorite, Ingredient, Recipe, RecipeIngredient, ShoppingCart, Tag
)
from .pagination import Pagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    FavoriteSerializer, IngredientSerializer, RecipeCreateSerializer,
    RecipeListSerializer, ShoppingCartSerializer, TagSerializer
)

User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = Pagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return RecipeCreateSerializer
        return RecipeListSerializer

    def _add_or_remove(self, serializer_class, model, request, pk):
        recipe = self.get_object()
        if request.method == 'POST':
            serializer = serializer_class(
                data={'user': request.user.id, 'recipe': recipe.id},
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                serializer.data, status=status.HTTP_201_CREATED
            )
        model.objects.filter(
            user=request.user, recipe=recipe
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True, methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk=None):
        return self._add_or_remove(FavoriteSerializer, Favorite, request, pk)

    @action(
        detail=True, methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk=None):
        return self._add_or_remove(
            ShoppingCartSerializer, ShoppingCart, request, pk
        )

    @action(
        detail=False, methods=('get',),
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        ingredients = RecipeIngredient.objects.filter(
            recipe__in=request.user.shopping_cart.values('recipe')
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(total_amount=Sum('amount')).order_by('ingredient__name')

        content = 'Список покупок:\n' + '\n'.join(
            '- {} ({}) — {}'.format(
                item['ingredient__name'],
                item['ingredient__measurement_unit'],
                item['total_amount']
            )
            for item in ingredients
        )
        response = HttpResponse(
            content, content_type='text/plain; charset=utf-8'
        )
        response['Content-Disposition'] = (
            'attachment; filename="shopping_cart.txt"'
        )
        return response

    @action(
        detail=True, methods=('get',), permission_classes=(AllowAny,),
        url_path='get-link', url_name='get-link'
    )
    def get_link(self, request, pk=None):
        recipe = self.get_object()
        if not recipe.short_link:
            recipe.generate_short_link()
        short_url = request.build_absolute_uri(
            reverse('short-url', args=(recipe.short_link,))
        )
        return Response({'short-link': short_url})
