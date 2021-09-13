import django_filters

from .models import Recipe


class RecipesFilter(django_filters.FilterSet):
    tags = django_filters.CharFilter(
        field_name='tags__slug',
    )

    author = django_filters.CharFilter(
        field_name='author__id',
    )
    name = django_filters.CharFilter(
        field_name='ingredients__name',
        lookup_expr='icontains'
    )

    is_favorited = django_filters.BooleanFilter(
        field_name='favorites__recipe',
        method='filter_is_favorited',
    )
    is_in_shopping_cart = django_filters.BooleanFilter(
        field_name='shop_carts__recipe',
        method='filter_is_in_shopping_cart',
    )

    class Meta:
        model = Recipe
        fields = (
            'is_favorited',
            'tags',
            'is_in_shopping_cart',
            'author',
            'ingredients'
        )

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        return queryset.filter(
            recipes__user=user,
            **{name: value}
        )

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        return queryset.filter(
            shop_carts__user=user,
            **{name: value}
        )
