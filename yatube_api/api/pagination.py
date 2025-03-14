from rest_framework.pagination import LimitOffsetPagination


class PostPagination(LimitOffsetPagination):
    """Кастомный пагинатор с поддержкой limit и offset."""

    default_limit = 10
    max_limit = 100

    def paginate_queryset(self, queryset, request, view=None):
        """Применяет пагинацию только при наличии параметров."""
        if 'limit' in request.query_params or 'offset' in request.query_params:
            return super().paginate_queryset(queryset, request, view)
        return None
