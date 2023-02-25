from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField

from user.serializers import CustomUserSerializer
from .models import Tag, Recipe, Ingredients, FavoriteRecipe, IngredientRecipe, ShoppingCart
from user.models import Follow, User


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngridientSerealizator(serializers.ModelSerializer):

    class Meta:
        model = Ingredients
        fields = (
            'id', 'name', 'measurement_unit'
        )

class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(
        source='ingredient.id',
    )
    name = serializers.ReadOnlyField(
        source='ingredient.name',
    )
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit',
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class  FavoriteSerealizator(serializers.ModelSerializer):
    recipe = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all()
    )
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all()
    )

    class Meta:
        model = FavoriteRecipe
        fields = (
            'id', 'name', 'image', 'cooking_time'
        )


class ShoppingCartSerializer(FavoriteSerealizator):

    class Meta:
        model = ShoppingCart
        fields = ['recipe', 'user']


class FollowSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault()
    )
    following = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()
    )
    validators = [
        UniqueTogetherValidator(
            queryset=Follow.objects.select_related('user'),
            fields=['user', 'following']
        )
    ]

    def validate(self, data):
        if self.context['request'].user != data.get('following'):
            return data
        raise serializers.ValidationError(
            'Нельзя подписаться на себя'
        )

    class Meta:
        fields = ('__all__')
        model = Follow
