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
        lookup_expr='isnull'
    )

    def filter_is_favorited(self, queryset, name, value):
        lookup = '__'.join([name, 'isnull'])
        user = self.request.user
        user_recipes = user.favorites.all()
        user_recipes_id = [i.recipe.id for i in user_recipes]
        return queryset.filter(
            id__in=user_recipes_id,
            **{lookup: not(value)}
        )

    is_in_shopping_cart = django_filters.BooleanFilter(
        field_name='wishlist_recipe__recipe',
        method='filter_is_in_shopping_cart',
        lookup_expr='isnull'
    )

    def filter_is_in_shopping_cart(self, queryset, name, value):
        lookup = '__'.join([name, 'isnull'])
        user = self.request.user
        user_recipes = user.shop_carts.all()
        user_recipes_id = [i.recipe.id for i in user_recipes]
        return queryset.filter(
            id__in=user_recipes_id,
            **{lookup: not(value)}
        )

    class Meta:
        model = Recipe
        fields = (
            'is_favorited',
            'tags',
            'is_in_shopping_cart',
            'author',
            'name'
        )
