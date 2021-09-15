from collections import defaultdict
from datetime import datetime

from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .filter import RecipesFilter
from .models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                     ShopingCart, Tag)
from .permissions import IsAuthorOrReadOnly
from .serializers import (CreateRecipeSerializer, FavoriteSerializer,
                          GetRecipeSerializer, IngredientSerializer,
                          ShoppingCartSerializer, TagSerializer)

User = get_user_model()


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = CreateRecipeSerializer
    permission_classes = (IsAuthorOrReadOnly, )
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipesFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return GetRecipeSerializer
        return self.serializer_class


class IngredientViewSet(mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    pagination_class = None
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class TagViewSet(mixins.ListModelMixin,
                 mixins.RetrieveModelMixin,
                 viewsets.GenericViewSet):
    pagination_class = None
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class ShopingCartView(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, recipe_id):
        data = {'id': recipe_id, 'user': request.user.id}
        serializer = ShoppingCartSerializer(
            data=data,
            context={'request': request},
            partial=True
        )
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    def delete(self, request, recipe_id):
        user = request.user
        cart = get_object_or_404(
            ShopingCart,
            user=user,
            recipe_id=recipe_id
        )
        cart.delete()
        return Response(
            {'detail': 'рецпт удален из списка покупок'},
            status=status.HTTP_204_NO_CONTENT
        )


class FavoriteView(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, recipe_id):
        data = {'id': recipe_id, 'user': request.user.id}
        serializer = FavoriteSerializer(
            data=data,
            context={'request': request},
            partial=True
        )
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    def delete(self, request, recipe_id):
        user = request.user
        cart = get_object_or_404(
            Favorite,
            user=user,
            recipe_id=recipe_id
        )
        cart.delete()
        return Response(
            {'detail': 'рецпт удален из избранного'},
            status=status.HTTP_204_NO_CONTENT
        )


class DownloadShoppingCart(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        user = request.user
        recipes_id = ShopingCart.objects.filter(
            user_id=user.id).values_list("recipe", flat=True)
        ingredient_filter = IngredientRecipe.objects.filter(
            recipe_id__in=recipes_id).order_by('ingredient')

        ingredients = defaultdict(int)
        for ingredient in ingredient_filter:
            ingredients[ingredient.ingredient] += ingredient.amount
        current_date = datetime.now().date()
        wishlist = [f"Список покупок на {current_date} \n", "\n"]
        for ingredient, quantity in ingredients.items():
            wishlist.append(f'{ingredient.name} - {quantity}'
                            f'{ingredient.measurement_unit} \n')
        wishlist.append('\n\n')

        wishlist.append(f'foodgram {current_date.year}')

        response = HttpResponse(wishlist, 'Content-Type: text/plain')
        response['Content-Disposition'] = 'attachment; filename="wishlist.txt"'
        return response
