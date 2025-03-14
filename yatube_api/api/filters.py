from django_filters import rest_framework as filters

from posts.models import Follow


class FollowFilter(filters.FilterSet):
    """Фильтр для поиска фоловеров."""

    search = filters.CharFilter(
        field_name='following__username',
        lookup_expr='icontains'
    )

    class Meta:
        model = Follow
        fields = ['search']
