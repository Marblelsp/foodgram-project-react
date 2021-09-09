from django.contrib.auth import get_user_model
from rest_framework import serializers

from recipes.models import Recipe

from .models import Follow

from drf_extra_fields.fields import Base64ImageField

User = get_user_model()


class CustomUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        fields = (
            "email", "id", "username", "first_name",
            "last_name", "is_subscribed"
        )
        model = User

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        user = request.user
        if request is None or user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, following=obj).exists()


class ShowFollowerRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(max_length=None, use_url=True, required=False)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class ShowFollowersSerializer(serializers.ModelSerializer):
    recipes = ShowFollowerRecipeSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'recipes'
        )


class FollowSerializer(serializers.ModelSerializer):
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()
    recipes = ShowFollowerRecipeSerializer(many=True, read_only=True)

    class Meta:
        model = Follow
        fields = (
            'id',
            'recipes',
            'is_subscribed',
            'recipes_count',
            'user',
            'following'
        )

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
        return Follow.objects.create(user=user, following=following)

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


class FollowGetSerializerTest(serializers.ModelSerializer):
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()
    recipes = ShowFollowerRecipeSerializer(many=True)

    class Meta:
        model = User
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
