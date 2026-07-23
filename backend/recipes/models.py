import random
import string

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class NamedModel(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название')

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class Tag(NamedModel):
    slug = models.SlugField(
        max_length=200, unique=True, verbose_name='Slug'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        constraints = (
            models.UniqueConstraint(
                fields=('name',), name='unique_tag_name'
            ),
        )


class Ingredient(NamedModel):
    measurement_unit = models.CharField(
        max_length=200, verbose_name='Единица измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(NamedModel):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='recipes', verbose_name='Автор'
    )
    image = models.ImageField(
        upload_to='recipes/images/', verbose_name='Картинка'
    )
    text = models.TextField(verbose_name='Описание')
    ingredients = models.ManyToManyField(
        Ingredient, through='RecipeIngredient',
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(Tag, verbose_name='Теги')
    cooking_time = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Время приготовления (мин)'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True, verbose_name='Дата публикации'
    )
    short_link = models.CharField(
        max_length=10, unique=True, blank=True, default='',
        verbose_name='Короткая ссылка'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def generate_short_link(self):
        chars = string.ascii_letters + string.digits
        while True:
            short = ''.join(random.choices(chars, k=6))
            if not Recipe.objects.filter(short_link=short).exists():
                break
        self.short_link = short
        self.save()

    def get_favorites_count(self):
        return self.favorite.count()


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='recipe_ingredients', verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE,
        related_name='recipe_ingredients', verbose_name='Ингредиент'
    )
    amount = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Количество'
    )

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецептов'
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique_recipe_ingredient'
            ),
        )

    def __str__(self):
        return f'{self.ingredient} — {self.amount}'


class UserRecipeBase(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name='Рецепт'
    )

    class Meta:
        abstract = True
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_%(class)s'
            ),
        )

    def __str__(self):
        return f'{self.user} — {self.recipe}'


class Favorite(UserRecipeBase):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='favorite', verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='favorite', verbose_name='Рецепт'
    )

    class Meta(UserRecipeBase.Meta):
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'


class ShoppingCart(UserRecipeBase):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='shoppingcart', verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='shoppingcart', verbose_name='Рецепт'
    )

    class Meta(UserRecipeBase.Meta):
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
