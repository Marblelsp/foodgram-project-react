from django.contrib.auth import get_user_model
from django.db.models.deletion import PROTECT
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from users.models import CustomUser

from .models import (Favorite, Follow, Ingredient, IngredientRecipe, Recipe,
                     ShopingCart, Tag)

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['id', 'name', 'color', 'slug']
        model = Tag


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Ingredient


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="ingredient.id")

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientRecipeSerializer(
        many=True,
        source='ingredient_recipe',
    )
    image = Base64ImageField(max_length=None, use_url=True, required=False)

    class Meta:
        fields = (
            'id', 'ingredients', 'tags', 'image',
            'name', 'text', 'cooking_time'
        )
        model = Recipe

    def update(self, instance, validated_data):
        context = self.context['request']
        tags = validated_data.pop("tags")
        ingredients_input = context.data['ingredients']
        del validated_data['ingredient_recipe']

        instance.author = self.context.get('request').user
        for item in validated_data:
            if Recipe._meta.get_field(item):
                setattr(instance, item, validated_data[item])
        instance.tags.set(tags)
        IngredientRecipe.objects.filter(recipe=instance).delete()

        new_ingredient_recipes = []
        for ingredient in ingredients_input:
            ingredient_model = get_object_or_404(
                Ingredient,
                id=ingredient['id']
            )
            new_ingredient_recipes.append(
                IngredientRecipe(
                    recipe=instance,
                    ingredient=ingredient_model,
                    amount=ingredient['amount'],
                )
            )
        IngredientRecipe.objects.bulk_create(new_ingredient_recipes)
        instance.save()
        return instance

    def create(self,  validated_data):
        context = self.context['request']
        author = context.user
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredient_recipe")
        recipe = Recipe.objects.create(**validated_data, author=author)
        recipe.tags.set(tags)
        for ingredient in ingredients:
            ingredient_model = Ingredient.objects.get(
                id=ingredient['ingredient']['id']
            )
            IngredientRecipe.objects.create(
                recipe=recipe,
                ingredient=ingredient_model,
                amount=ingredient["amount"],
            )
        return recipe


class IngredientGetRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(
        source="ingredient.id"
    )
    name = serializers.CharField(
        read_only=True,
        source="ingredient.name"
    )
    measurement_unit = serializers.CharField(
        read_only=True,
        source="ingredient.measurement_unit"
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class CustomUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        fields = [
            "email", "id", "username", "first_name",
            "last_name", "is_subscribed"
        ]
        model = CustomUser

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        user = request.user
        if request is None or user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, following=obj).exists()


class GetRecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientGetRecipeSerializer(
        many=True,
        source='ingredient_recipe'
    )
    tags = TagSerializer(many=True)
    author = CustomUserSerializer()
    image = Base64ImageField(max_length=None, use_url=True, required=False)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        fields = [
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image',
            'text', 'cooking_time',
        ]
        model = Recipe

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        user = request.user
        if request is None or user.is_anonymous:
            return False
        return ShopingCart.objects.filter(recipe=obj, user=user).exists()

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        user = request.user
        if request is None or user.is_anonymous:
            return False
        return Favorite.objects.filter(recipe=obj, user=user).exists()


class ShowFollowerRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(max_length=None, use_url=True, required=False)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class ShowFollowersSerializer(serializers.ModelSerializer):
    recipes = ShowFollowerRecipeSerializer(many=True, read_only=True)

    class Meta:
        model = CustomUser
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'recipes'
        )


class ShoppingListSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(
        source="recipe.id"
    )
    name = serializers.CharField(
        read_only=True,
        source="recipe.name"
    )
    cooking_time = serializers.CharField(
        read_only=True,
        source="recipe.cooking_time"
    )

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(serializers.ModelSerializer):
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()
    recipes = ShowFollowerRecipeSerializer(many=True, read_only=True)

    class Meta:
        model = Follow
        fields = ('id',  'recipes', 'is_subscribed', 'recipes_count', 'user', 'following')

    def validate(self, data):
        following = data.get('following')
        user = self.context['request'].user
        if Follow.objects.filter(user=user, following=following).exists():
            raise serializers.ValidationError({
                'errors': 'Вы уже подписались на данного пользователя'
            })
        elif user == following:
            raise serializers.ValidationError({
                'errors': 'Нельзя подписаться на самого себя'
            })
        return data

    def create(self, validated_data):
        following = validated_data.get('following')
        user = self.context['request'].user
        recipes_cart = Follow.objects.create(user=user, following=following)
        return recipes_cart

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None:
            return False
        return Follow.objects.filter(
            user=request.user,
            following=obj.following
        ).exists()

    def get_recipes_count(self, obj):
        return obj.following.recipes.count()


class ShoppingCartSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(
        source="recipe.id"
    )
    name = serializers.CharField(
        read_only=True,
        source="recipe.name"
    )
    cooking_time = serializers.CharField(
        read_only=True,
        source="recipe.cooking_time"
    )
    image = Base64ImageField(source="recipe.image", max_length=None, use_url=True, required=False)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')

    def validate(self, data):
        request = self.context.get('request')
        user = request.user
        recipe = data['recipe']['id']
        if ShopingCart.objects.filter(user=user, recipe_id=recipe).exists():
            raise serializers.ValidationError({
                'errors': 'рецепт уже добавлен в список покупок'
            })
        return data

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        recipe = validated_data['recipe']['id']
        recipes_cart = ShopingCart.objects.create(user=user, recipe_id=recipe)
        return recipes_cart


class FavoriteSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(
        source="recipe.id"
    )
    name = serializers.CharField(
        read_only=True,
        source="recipe.name"
    )
    cooking_time = serializers.CharField(
        read_only=True,
        source="recipe.cooking_time"
    )
    image = Base64ImageField(source="recipe.image", max_length=None, use_url=True, required=False)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')

    def validate(self, data):
        request = self.context.get('request')
        user = request.user
        recipe = data['recipe']['id']
        if Favorite.objects.filter(user=user, recipe_id=recipe).exists():
            raise serializers.ValidationError({
                'errors': 'рецепт уже добавлен в избранное'
            })
        return data

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        recipe = validated_data['recipe']['id']
        recipes_cart = Favorite.objects.create(user=user, recipe_id=recipe)
        return recipes_cart



class FollowGetSerializerTest(serializers.ModelSerializer):
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()
    recipes = ShowFollowerRecipeSerializer(many=True)

    class Meta:
        model = CustomUser
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', "is_subscribed", 'recipes', 'recipes_count'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None:
            return False
        return Follow.objects.filter(
            user=request.user,
            following=obj
        ).exists()

    def get_recipes_count(self, obj):
        return obj.recipes.count()
