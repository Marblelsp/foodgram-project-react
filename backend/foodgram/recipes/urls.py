from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (DownloadShoppingCart, FollowView, IngredientViewSet,
                    RecipeViewSet, TagViewSet, FavoriteView, my_subscriptions,
                    ShopingCartView)

v1_router = DefaultRouter()
v1_router.register('recipes', RecipeViewSet, basename='recipes')
v1_router.register('tags', TagViewSet, basename='tags')
v1_router.register('ingredients', IngredientViewSet, basename='ingredients')


urlpatterns = [
    path(
        'recipes/download_shopping_cart/',
        DownloadShoppingCart.as_view()
    ),
    path(
        'recipes/<int:recipe_id>/favorite/',
        FavoriteView.as_view(),
        name='my_favorite'
    ),
    path(
        'recipes/<int:recipe_id>/shopping_cart/',
        ShopingCartView.as_view(), name='shopping_cart'
    ),
    path('', include(v1_router.urls)),
    path(
        'users/subscriptions/',
        my_subscriptions
    ),
    path(
        'users/<int:user_id>/subscribe/',
        FollowView.as_view()
    ),
]
