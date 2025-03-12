from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, viewsets
from rest_framework.exceptions import ValidationError

from posts.models import Comment, Group, Post, Follow
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    CommentSerializer,
    GroupSerializer,
    PostSerializer,
    FollowSerializer,
)
from api.pagination import PostPagination


class PostViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с постами."""

    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsAuthorOrReadOnly,
    ]
    pagination_class = PostPagination

    def get_queryset(self):
        """Проверяет на наличие лимита и офсета в запросе."""
        queryset = super().get_queryset()
        if (
            'limit' in self.request.query_params
            or 'offset' in self.request.query_params
        ):
            self.pagination_class = PostPagination
        else:
            self.pagination_class = None
        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для работы с группами (только чтение)."""

    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [
        IsAuthorOrReadOnly,
        permissions.IsAuthenticatedOrReadOnly,
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
    """ViewSet для работы с фоловерами."""
    serializer_class = FollowSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['following__username']

    def get_queryset(self):
        """Фильтрует фоловеров."""
        queryset = Follow.objects.filter(user=self.request.user)
        search_query = self.request.query_params.get('search', None)
        if search_query:
            queryset = queryset.filter(
                following__username__icontains=search_query
            )
        return queryset

    def perform_create(self, serializer):
        """Создает подписки и проверяет их корректность."""
        user = self.request.user
        following = serializer.validated_data['following']
        if user == following:
            raise ValidationError('Нельзя подписаться на самого себя.')
        if Follow.objects.filter(user=user, following=following).exists():
            raise ValidationError('Вы уже подписаны на этого пользователя.')
        serializer.save(user=user)
