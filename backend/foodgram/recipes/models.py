from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from pytils.translit import slugify

User = get_user_model()


class Tag(models.Model):
    name = models.CharField("Название", max_length=200)
    color = models.CharField("Цвет", max_length=200, blank=True)
    slug = models.SlugField("URL", max_length=200, unique=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:100]
        super().save(*args, **kwargs)


class Ingredient(models.Model):
    name = models.CharField("Название", max_length=200)
    measurement_unit = models.CharField(
        "Единица измерения",
        max_length=10
    )

    def __str__(self):
        return self.name[:15]


class Recipe(models.Model):
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        related_name='recipes'
    )
    tags = models.ManyToManyField(Tag, blank=True)
    image = models.ImageField(
        "Картинка",
        help_text="Добавьте картинку к посту",
        upload_to="recipes/",
        blank=True,
        null=True,
    )
    name = models.CharField("Название", max_length=200)
    text = models.TextField("Описание", max_length=3000)
    cooking_time = models.PositiveSmallIntegerField(
        "время приготовления в минутах",
        default=30,
        validators=[MinValueValidator(1, 'Меньше 1 поставить нельзя')],
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    pub_date = models.DateTimeField(
        "Дата публикации",
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        ordering = ["-pub_date"]

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name="recipe_ingredients"
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="recipe_ingredients"
    )
    amount = models.PositiveSmallIntegerField(
        default=1,
        validators=[MinValueValidator(1, 'Меньше 1 поставить нельзя')],
        verbose_name='Количество ингредиента'
    )


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="favorites"
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="favorites"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"],
                name="unique_author_user_favorite")
        ]


class ShopingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="shop_carts"
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="shop_carts"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"],
                name="unique_author_user_shopcart")
        ]
