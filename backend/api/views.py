from django.contrib.auth import get_user_model
from django.db.models import Exists, F, OuterRef, Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from recipes.models import (
    Favorite, Ingredient, Recipe, RecipeIngredient, ShoppingCart, Tag
)

from .filters import IngredientFilter, RecipeFilter
from .pagination import Pagination
from .permissions import IsAuthenticatedOrAuthorOrReadOnly
from .serializers import (
    AvatarSerializer, FavoriteSerializer, IngredientSerializer,
    RecipeCreateSerializer, RecipeListSerializer,
    ShoppingCartSerializer, SubscriptionCreateSerializer,
    SubscriptionSerializer, TagSerializer, UserSerializer
)

User = get_user_model()


class UserRelationMixin:

    def _add_or_remove(self, serializer_class, model, request, pk):
        recipe = self.get_object()
        if request.method == 'POST':
            serializer = serializer_class(
                data={'user': request.user.id, 'recipe': recipe.id},
                context=self.get_serializer_context()
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                serializer.data, status=status.HTTP_201_CREATED
            )
        model.objects.filter(user=request.user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ReadOnlyViewSet(viewsets.ReadOnlyModelViewSet):
    pagination_class = None


class UserViewSet(DjoserUserViewSet):
    pagination_class = Pagination

    @action(
        detail=False, methods=('get',),
        permission_classes=(IsAuthenticated,)
    )
    def me(self, request):
        serializer = UserSerializer(
            request.user,
            context=self.get_serializer_context()
        )
        return Response(serializer.data)

    @action(
        detail=False, methods=('get',),
        permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        queryset = User.objects.filter(
            id__in=request.user.follower.values('author')
        )
        page = self.paginate_queryset(queryset)
        serializer = SubscriptionSerializer(
            page, many=True, context=self.get_serializer_context()
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True, methods=('post',),
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, id=None):
        author = get_object_or_404(User, id=id)
        serializer = SubscriptionCreateSerializer(
            data={'user': request.user.id, 'author': author.id},
            context=self.get_serializer_context()
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            SubscriptionSerializer(
                author, context=self.get_serializer_context()
            ).data,
            status=status.HTTP_201_CREATED
        )

    @subscribe.mapping.delete
    def unsubscribe(self, request, id=None):
        author = get_object_or_404(User, id=id)
        request.user.follower.filter(author=author).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False, methods=('put',),
        permission_classes=(IsAuthenticated,), url_path='me/avatar'
    )
    def avatar(self, request):
        user = request.user
        serializer = AvatarSerializer(
            user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        avatar_url = None
        if user.avatar:
            avatar_url = request.build_absolute_uri(user.avatar.url)
        return Response({'avatar': avatar_url})

    @avatar.mapping.delete
    def delete_avatar(self, request):
        request.user.delete_avatar()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(ReadOnlyViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(ReadOnlyViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(UserRelationMixin, viewsets.ModelViewSet):
    permission_classes = (IsAuthenticatedOrAuthorOrReadOnly,)
    pagination_class = Pagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_queryset(self):
        user = self.request.user
        qs = Recipe.objects.all()
        if user.is_authenticated:
            qs = qs.annotate(
                is_favorited=Exists(
                    Favorite.objects.filter(
                        user=user, recipe=OuterRef('pk')
                    )
                ),
                is_in_shopping_cart=Exists(
                    ShoppingCart.objects.filter(
                        user=user, recipe=OuterRef('pk')
                    )
                )
            )
        return qs

    def get_serializer_class(self):
        if self.action in {'create', 'update', 'partial_update'}:
            return RecipeCreateSerializer
        return RecipeListSerializer

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
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        ingredients = RecipeIngredient.objects.filter(
            recipe__in=request.user.shopping_cart.values('recipe')
        ).values(
            name=F('ingredient__name'),
            unit=F('ingredient__measurement_unit')
        ).annotate(total_amount=Sum('amount')).order_by('name')

        content = '\n'.join(
            '- {name} ({unit}) — {total_amount}'.format(**item)
            for item in ingredients
        )
        content = f'Список покупок:\n{content}'
        return FileResponse(
            content.encode('utf-8'),
            content_type='text/plain; charset=utf-8',
            as_attachment=True,
            filename='shopping_cart.txt'
        )

    @action(
        detail=True, url_path='get-link', url_name='get-link'
    )
    def get_link(self, request, pk=None):
        recipe = self.get_object()
        if not recipe.short_link:
            recipe.generate_short_link()
        short_url = request.build_absolute_uri(
            reverse('short-url', args=(recipe.short_link,))
        )
        return Response({'short-link': short_url})
