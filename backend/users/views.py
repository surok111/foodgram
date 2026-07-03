from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from recipes.pagination import Pagination

from .serializers import (
    AvatarSerializer, SubscriptionCreateSerializer,
    SubscriptionSerializer, UserSerializer
)

User = get_user_model()


class UserViewSet(DjoserUserViewSet):
    pagination_class = Pagination

    @action(
        detail=False, methods=('get',),
        permission_classes=(IsAuthenticated,)
    )
    def me(self, request):
        serializer = UserSerializer(
            request.user, context={'request': request}
        )
        return Response(serializer.data)

    @action(
        detail=False, methods=('get',),
        permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        queryset = request.user.follower.values('author')
        users = User.objects.filter(id__in=queryset)
        page = self.paginate_queryset(users)
        serializer = SubscriptionSerializer(
            page, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True, methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, id=None):
        author = get_object_or_404(User, id=id)
        if request.method == 'POST':
            serializer = SubscriptionCreateSerializer(
                data={'user': request.user.id, 'author': author.id},
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                SubscriptionSerializer(
                    author, context={'request': request}
                ).data,
                status=status.HTTP_201_CREATED
            )
        request.user.follower.filter(author=author).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False, methods=('put', 'delete'),
        permission_classes=(IsAuthenticated,), url_path='me/avatar'
    )
    def avatar(self, request):
        user = request.user
        if request.method == 'PUT':
            serializer = AvatarSerializer(
                user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            avatar_url = None
            if user.avatar:
                avatar_url = request.build_absolute_uri(user.avatar.url)
            return Response({'avatar': avatar_url})
        user.delete_avatar()
        return Response(status=status.HTTP_204_NO_CONTENT)
