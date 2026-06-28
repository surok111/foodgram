from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import User, Subscription
from .serializers import (
    CustomUserSerializer, SetAvatarSerializer, SubscriptionSerializer
)


class CustomUserViewSet(UserViewSet):

    def get_permissions(self):
        if self.action in ('list', 'retrieve', 'create'):
            return []
        return [IsAuthenticated()]

    @action(
        detail=False, methods=['get'],
        permission_classes=[IsAuthenticated],
        url_path='me'
    )
    def me(self, request):
        serializer = CustomUserSerializer(
            request.user, context={'request': request}
        )
        return Response(serializer.data)

    @action(
        detail=False, methods=['put'],
        permission_classes=[IsAuthenticated],
        url_path='me/avatar'
    )
    def avatar(self, request):
        serializer = SetAvatarSerializer(
            request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        avatar_url = request.build_absolute_uri(request.user.avatar.url)
        return Response({'avatar': avatar_url})

    @avatar.mapping.delete
    def delete_avatar(self, request):
        user = request.user
        if user.avatar:
            user.avatar.delete()
            user.avatar = None
            user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False, methods=['get'],
        permission_classes=[IsAuthenticated],
        url_path='subscriptions'
    )
    def subscriptions(self, request):
        queryset = User.objects.filter(subscribing__user=request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = SubscriptionSerializer(
                page, many=True, context={'request': request}
            )
            return self.get_paginated_response(serializer.data)
        serializer = SubscriptionSerializer(
            queryset, many=True, context={'request': request}
        )
        return Response(serializer.data)

    @action(
        detail=True, methods=['post'],
        permission_classes=[IsAuthenticated],
        url_path='subscribe'
    )
    def subscribe(self, request, id=None):
        author = get_object_or_404(User, id=id)
        if request.user == author:
            return Response(
                {'errors': 'Нельзя подписаться на себя.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if Subscription.objects.filter(user=request.user, author=author).exists():
            return Response(
                {'errors': 'Вы уже подписаны на этого пользователя.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        Subscription.objects.create(user=request.user, author=author)
        serializer = SubscriptionSerializer(
            author, context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def unsubscribe(self, request, id=None):
        author = get_object_or_404(User, id=id)
        subscription = Subscription.objects.filter(
            user=request.user, author=author
        )
        if not subscription.exists():
            return Response(
                {'errors': 'Вы не подписаны на этого пользователя.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
