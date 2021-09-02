from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, serializers, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model

from .filter import RecipesFilter
from .models import Favorite, Follow, Ingredient, Recipe, ShopingCart, Tag
from .permissions import IsAuthorOrReadOnly
from .serializers import (FollowSerializer, GetRecipeSerializer,
                          IngredientSerializer, RecipeSerializer,
                          FavoriteSerializer, ShowFollowersSerializer,
                          TagSerializer, ShoppingCartSerializer, FollowGetSerializerTest)

User = get_user_model()


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthorOrReadOnly]
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
    permission_classes = (IsAuthenticated,)

    def get(self, request, recipe_id):
        data = {'id': recipe_id}
        serializer = ShoppingCartSerializer(data=data, context={'request': request}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    def delete(self, request, recipe_id):
        user = request.user.id
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
    permission_classes = (IsAuthenticated,)

    def get(self, request, recipe_id):
        data = {'id': recipe_id}
        serializer = FavoriteSerializer(data=data, context={'request': request}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    def delete(self, request, recipe_id):
        user = request.user.id
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


class FollowView(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request, user_id):
        following = get_object_or_404(User, id=user_id)
        data = {'id': request.user.id, 'following': user_id}
        serializer = FollowSerializer(data=data, context={'request': request}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response = FollowGetSerializerTest(following)
        return Response(
            response.data,
            status=status.HTTP_201_CREATED
        )

    def delete(self, request, user_id):
        user = request.user
        following = User.objects.get(id=user_id)
        follow = get_object_or_404(
        Follow,
        user=user,
        following=following
        )
        follow.delete()
        return Response(
            {'detail': 'Подписка отменена'},
            status=status.HTTP_204_NO_CONTENT
        )


@api_view(['GET', ])
@permission_classes([IsAuthenticated, ])
def my_subscriptions(request):
    user = request.user
    following = user.follower.all()
    user_obj = []
    for follow_obj in following:
        user_obj.append(follow_obj.following)
    paginator = PageNumberPagination()
    paginator.page_size = 10
    result_page = paginator.paginate_queryset(user_obj, request)
    serializer = ShowFollowersSerializer(
        result_page, many=True, context={'current_user': request.user})
    return paginator.get_paginated_response(serializer.data)


class DownloadShoppingCart(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        wishlist = []
        user = request.user
        user_recipes = user.shop_carts.all()
        recipes = [recipe.recipe.ingredients.name for recipe in user_recipes]
        print(recipes)

        ''''
        for i in recipes_all:
            for j in i.ingredientrecipe_set.all():
                wishlist.append(
                    f"{j.ingredient} {j.amount}"
                    f"{j.ingredient.measurement_unit} \n"
                )

        length = len(wishlist)
        new_wishlist = [i.split() for i in wishlist]

        for count in range(length):
            for count_2 in range(length):
                if count == count_2:
                    continue
                if new_wishlist[count][0] == new_wishlist[count_2][0]:
                    print(new_wishlist[count][1])
                    s = int(new_wishlist[count][1])
                    + int(new_wishlist[count_2][1])
                    new_wishlist[count][1] = str(s)
                    new_wishlist[count_2] = ['', '0']

        result = []
        for note in new_wishlist:
            if note[1] != '0':
                result.append(" ".join(note))
        result.append('Foodgram 2021')
        result = "\n".join(result)
        '''
        result = []
        response = HttpResponse(result, 'Content-Type: text/plain')
        response['Content-Disposition'] = 'attachment; filename="wishlist.txt"'
        return response
