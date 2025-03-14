from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, viewsets

from posts.models import Comment, Group, Post, Follow
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    CommentSerializer,
    GroupSerializer,
    PostSerializer,
    FollowSerializer,
)
from .pagination import PostPagination
from .filters import FollowFilter


class PostViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с постами."""

    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsAuthorOrReadOnly,
    ]
    pagination_class = PostPagination

    def perform_create(self, serializer):
        """Создает пост и устанавливает автора."""
        serializer.save(author=self.request.user)


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для работы с группами (только чтение)."""

    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsAuthorOrReadOnly,
    ]


class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с комментариями."""

    serializer_class = CommentSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsAuthorOrReadOnly,
    ]

    def get_queryset(self):
        """Возвращает комментарии для конкретного поста."""
        post_id = self.kwargs["post_id"]
        return Comment.objects.filter(post_id=post_id)

    def perform_create(self, serializer):
        """Создает комментарий для конкретного поста."""
        post_id = self.kwargs["post_id"]
        post = get_object_or_404(Post, id=post_id)
        serializer.save(author=self.request.user, post=post)


class FollowViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с подписками."""

    serializer_class = FollowSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = FollowFilter
    http_method_names = ['get', 'post']

    def get_queryset(self):
        """Возвращает подписки текущего пользователя."""
        return Follow.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Создает подписку и проверяет её корректность."""
        serializer.save(user=self.request.user)
