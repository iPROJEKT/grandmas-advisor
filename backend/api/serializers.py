from rest_framework import serializers
from colorfield.fields import ColorField
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (
    Tag,
    Recipe,
    FavoriteRecipe,
    Ingredients,
    IngredientRecipe,
    ShoppingCart,
)
from user.serializers import CustomUserSerializer
from user.models import User, Follow


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'slug']


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredients
        fields = ['id', 'name', 'measurement_unit']


class AddIngredientInRecipeSerializer(
    serializers.ModelSerializer
):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredients.objects.all().order_by(
            'name'
        )
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')


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


class CreateRecipeSerializer(serializers.ModelSerializer):
    image = ColorField(max_length=None, use_url=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = AddIngredientInRecipeSerializer(many=True)
    cooking_time = serializers.IntegerField()
    tags = serializers.SlugRelatedField(
        many=True, 
        queryset=Tag.objects.all().order_by('name'),
        slug_field='id'
    )

    def validate_cooking_time(self, data):
        if data <= 0:
            raise serializers.ValidationError(
                'Время приготовления должно быть больше 0'
            )
        return data

    def create(self, validated_data):
        recipe = Recipe.objects.create(
            author=self.context.get(
                'request'
            ).user,
            **validated_data.pop(
                'ingredients'
            )
        )
        for ingredient in validated_data.pop('ingredients'):
            IngredientRecipe.objects.create(
                ingredient=ingredient['id'],
                recipe=recipe,
                amount=ingredient['amount']
            )
        recipe.tags.set(validated_data.pop('tags'))
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        IngredientRecipe.objects.filter(recipe=instance).delete()
        for ingredient in ingredients_data:
            IngredientRecipe.objects.create(
                ingredient=ingredient['id'],
                recipe=instance,
                amount=ingredient['amount']
            )
        instance.name = validated_data.pop('name')
        instance.text = validated_data.pop('text')
        if validated_data.get('image') is not None:
            instance.image = validated_data.pop('image')
        instance.cooking_time = validated_data.pop('cooking_time')
        instance.tags.set(tags_data)
        instance.save()
        return instance

    class Meta:
        model = Recipe
        fields = [
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
        ]


class FavoriteSerializer(serializers.ModelSerializer):
    recipe = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all()
    )
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.select_related(
            'recipes', 'ingredients'
        )
    )

    class Meta:
        model = FavoriteRecipe
        fields = ['recipe', 'user']


class ShoppingCartSerializer(FavoriteSerializer):

    class Meta:
        model = ShoppingCart
        fields = ['recipe', 'user']


class ShowRecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(read_only=True, many=True)
    image = ColorField()
    author = CustomUserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField('get_ingredients')
    is_favorited = serializers.SerializerMethodField('get_is_favorited')
    is_in_shopping_cart = serializers.SerializerMethodField(
        "get_is_in_shopping_cart"
    )

    def get_ingredients(self, obj):
        return IngredientInRecipeSerializer(
            IngredientRecipe.objects.filter(recipe=obj),
            many=True
        ).data

    def get_is_favorited(self, obj):
        if self.context.get(
            'request'
        ) is None or self.context.get('request').user.is_anonymous:
            return False
        return FavoriteRecipe.objects.filter(
            recipe=obj,
            user=self.context.get('request').user
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        if self.context.get(
            'request'
        ) is None or self.context.get('request').user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            recipe=obj,
            user=self.context.get('request').user
        ).exists()

    class Meta:
        model = Recipe
        fields = [
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        ]


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
