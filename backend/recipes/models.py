from django.db import models
from django.conf import settings
from django.core import validators
from colorfield.fields import ColorField

from .validators import is_valid_hexa_code
from user.models import User


class Tag(models.Model):
    name = models.CharField(
        unique=True,
        max_length=settings.NAME_MAX_LENGTH,
    )
    color = ColorField(
        validators=[is_valid_hexa_code],
        unique=True,
    )
    slug = models.SlugField(
        unique=True,
        max_length=settings.MAX_SLUG_LEIGHT
    )


class Ingredients(models.Model):
    name = models.CharField(
        max_length=settings.NAME_MAX_LENGTH,
    )
    measurement_unit = models.CharField(
        max_length=settings.NAME_MAX_LENGTH,
    )


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        related_name='recipe',
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
    text = models.TextField(
        'Описание рецепта',
    )
    tags = models.ManyToManyField(
        Tag,
        max_length=settings.NAME_MAX_LENGTH
    )
    cooking_time = models.IntegerField(
        validators=[
            validators.MinValueValidator(
                1,
                message='Минимальное время приготовления 1 минута'
            ), 
        ])


class IngredientRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )
    ingredients = models.ForeignKey(
        Ingredients,
        on_delete=models.CASCADE,
        related_name='ingredients',
    )
    amount = models.PositiveSmallIntegerField(
        default=1,
        validators=[
            validators.MinValueValidator(
                1,
                message='Минимальное число единиц - 1'
            ),
        ])

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    'recipe',
                    'ingredients'
                ],
                name='unique ingredient'
            )
        ]


class FavoriteRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='is_favorited',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        related_name = '+'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    'recipe',
                    'user'
                ],
                name='unique recipe'
            )
        ]


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name = '+'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='is_in_shopping_cart',
    )

    class Meta:
        ordering = ('-recipe',)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_cart'
            )
        ]
