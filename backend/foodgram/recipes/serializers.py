from django.contrib.auth import get_user_model
from django.db import transaction
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from users.serializers import CustomUserSerializer
from .models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                     ShopingCart, Tag)

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Tag


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Ingredient


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source="ingredient",
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')


class CreateRecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientRecipeSerializer(
        many=True,
        source='recipe_ingredients',
    )
    image = Base64ImageField(max_length=None, use_url=True, required=False)

    class Meta:
        fields = (
            'id', 'ingredients', 'tags', 'image',
            'name', 'text', 'cooking_time'
        )
        model = Recipe

    def create_ingredients_recipe(self, ingredients,
                                  new_recipe_ingredients, instance):
        for ingredient in ingredients:
            new_recipe_ingredients.append(
                IngredientRecipe(
                    recipe=instance,
                    ingredient=ingredient['ingredient'],
                    amount=ingredient['amount'],
                )
            )
        IngredientRecipe.objects.bulk_create(new_recipe_ingredients)

    @transaction.atomic
    def update(self, instance, validated_data):
        context = self.context['request']
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop('recipe_ingredients')
        instance.author = context.user

        for item in validated_data:
            if Recipe._meta.get_field(item):
                setattr(instance, item, validated_data[item])
        instance.tags.set(tags)
        instance.recipe_ingredients.all().delete()

        new_recipe_ingredients = []
        self.create_ingredients_recipe(
            ingredients,
            new_recipe_ingredients,
            instance
        )
        instance.save()
        return instance

    @transaction.atomic
    def create(self, validated_data):
        context = self.context['request']
        author = context.user
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("recipe_ingredients")
        recipe = Recipe.objects.create(**validated_data, author=author)
        recipe.tags.set(tags)

        new_recipe_ingredients = []
        self.create_ingredients_recipe(
            ingredients,
            new_recipe_ingredients,
            instance=recipe
        )
        return recipe

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        for ingredient_item in ingredients:
            if int(ingredient_item['amount']) <= 0:
                raise serializers.ValidationError({
                    'ingredients': ('Убедитесь, что значение количества '
                                    'ингредиента больше 0.')
                })
        return data

    def validate_cooking_time(self, data):
        cooking_time = self.initial_data.get('cooking_time')
        if int(cooking_time) <= 0:
            raise serializers.ValidationError(
                'Убедитесь, что время '
                'приготовления больше 0.'
            )

        return data

class IngredientGetRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source="ingredient",
        read_only=True
    )
    name = serializers.SlugRelatedField(
        read_only=True,
        slug_field='name',
        source='ingredient',
    )
    measurement_unit = serializers.SlugRelatedField(
        read_only=True,
        slug_field='measurement_unit',
        source="ingredient",
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class GetRecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientGetRecipeSerializer(
        many=True,
        source='recipe_ingredients'
    )
    tags = TagSerializer(many=True)
    author = CustomUserSerializer()
    image = Base64ImageField(max_length=None, use_url=True, required=False)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image',
            'text', 'cooking_time',
        )
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


class ShoppingCartSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source="recipe",
        queryset=Recipe.objects.all()
    )
    name = serializers.SlugRelatedField(
        queryset=Recipe.objects.all(),
        slug_field='name',
        source="recipe"
    )
    cooking_time = serializers.SlugRelatedField(
        queryset=Recipe.objects.all(),
        slug_field='cooking_time',
        source="recipe"
    )
    image = Base64ImageField(
        source="recipe.image",
        max_length=None,
        use_url=True,
        required=False
    )

    class Meta:
        model = ShopingCart
        fields = ('id', 'name', 'image', 'cooking_time', 'user', 'recipe', )
        validators = [
            UniqueTogetherValidator(
                queryset=ShopingCart.objects.all(),
                fields=('user', 'recipe'),
                message=('рецепт уже добавлен в список покупок')
            )
        ]

    def to_representation(self, obj):
        ret = super(ShoppingCartSerializer, self).to_representation(obj)
        del ret['user']
        del ret['recipe']
        return ret

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        recipe = validated_data['recipe']
        return ShopingCart.objects.create(user=user, recipe=recipe)


class FavoriteSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source="recipe",
        queryset=Recipe.objects.all()
    )
    name = serializers.SlugRelatedField(
        queryset=Recipe.objects.all(),
        slug_field='name',
        source="recipe"
    )
    cooking_time = serializers.SlugRelatedField(
        queryset=Recipe.objects.all(),
        slug_field='cooking_time',
        source="recipe"
    )
    image = Base64ImageField(
        source="recipe.image",
        max_length=None,
        use_url=True,
        required=False
    )

    class Meta:
        model = Favorite
        fields = ('id', 'name', 'image', 'cooking_time', 'user', 'recipe', )
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe'),
                message=('рецепт уже добавлен в избранное')
            )
        ]

    def to_representation(self, obj):
        ret = super(FavoriteSerializer, self).to_representation(obj)
        del ret['user']
        del ret['recipe']
        return ret

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        recipe = validated_data['recipe']
        return Favorite.objects.create(user=user, recipe=recipe)
