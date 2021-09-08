from django.contrib import admin

from .models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                     ShopingCart, Tag)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', )
    empty_value_display = '-пусто-'
    prepopulated_fields = {"slug": ("name",)}


@admin.register(IngredientRecipe)
class TagIngredientRecipe(admin.ModelAdmin):
    list_display = ('recipe', 'amount', )
    empty_value_display = '-пусто-'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit', )
    empty_value_display = '-пусто-'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'image', 'name', 'text', 'cooking_time',
        'author', 'pub_date', 'get_ingredients'
    )
    empty_value_display = '-пусто-'

    def get_ingredients(self, obj):
        return obj.ingredients.all()


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe', )
    empty_value_display = '-пусто-'


@admin.register(ShopingCart)
class ShopingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe', )
    empty_value_display = '-пусто-'
