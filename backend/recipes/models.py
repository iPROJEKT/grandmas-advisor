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

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Тэги'


class Ingredients(models.Model):
    name = models.CharField(
        max_length=settings.NAME_MAX_LENGTH,
    )
    measurement_unit = models.CharField(
        max_length=settings.NAME_MAX_LENGTH,
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'


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
        upload_to='media/recipes/images/',
        blank=False,
        null=False,
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

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


class IngredientRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
    )
    ingredient = models.ForeignKey(
        Ingredients,
        on_delete=models.CASCADE,
        related_name='ingredients',
        null=False,
        blank=False,
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
        verbose_name = 'Количество ингредиента в рецепте'
        verbose_name_plural = 'Количество ингредиентов в рецептах'
        constraints = [
            models.UniqueConstraint(
                fields=[
                    'recipe',
                    'ingredient'
                ],
                name='unique ingredients'
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
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
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
        verbose_name = 'Cписок покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_cart'
            )
        ]
