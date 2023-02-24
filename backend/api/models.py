from django.conf import settings
from django.core import validators
from django.db import models
from colorfield.fields import ColorField

from user.models import User
from .validator import min_valid_valuse, weight_valid


class Tag(models.Model):
    name = models.CharField(
        unique=True,
        max_length=settings.NAME_MAX_LENGTH,
    )
    color = ColorField(
        unique=True,
    )
    slug = models.SlugField(
        unique=True,
    )


class Ingredients(models.Model):
    title = models.CharField(
        max_length=settings.NAME_MAX_LENGTH,
    )
    weight = models.IntegerField(
        validators=[weight_valid]
    )


class Recipe(models.Model):
    autor = models.ForeignKey(
        User,
        related_name='recipes',
        on_delete=models.CASCADE,
    )
    name = models.CharField(
        max_length=settings.NAME_MAX_LENGTH
    )
    image = models.ImageField(
        upload_to='static/recipe/',
        blank=True,
        null=True,
    )
    ingredients = models.ManyToManyField(
        Ingredients,
        related_name='ingredients',
    )
    text = models.TextField(
        'Описание рецепта',
    )
    tags = models.CharField(
        Tag,
        max_length=settings.NAME_MAX_LENGTH
    )
    cooking_time = models.IntegerField(
        validators=[min_valid_valuse],
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
    )


class IngredientRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe',
    )
    ingredient = models.ForeignKey(
        Ingredients,
        on_delete=models.CASCADE,
        related_name='ingredient',
    )
    amount = models.PositiveSmallIntegerField(
        default=1,
        validators=()
    )


class FavoriteRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites_recipe',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        related_name='favorite_recipe',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
    )


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Рецепт для покупки',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата добавления',
    )

    class Meta:
        ordering = ('-recipe',)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_cart'
            )
        ]
