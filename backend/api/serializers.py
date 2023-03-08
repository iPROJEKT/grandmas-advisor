from rest_framework import serializers
from colorfield.fields import ColorField
from rest_framework.validators import UniqueTogetherValidator
from drf_base64.fields import Base64ImageField


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
        fields = ('id', 'amount', 'name', 'measurement_unit')


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredients.objects.all().order_by(
            'name'
        )
    )
    name = serializers.CharField(
        source='ingredient.name',
    )
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit',
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class CreateRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(max_length=None,)
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

    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientInRecipeSerializer(many=True,)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'image',
            'text',
            'cooking_time',
        )

    def get_ingredients(self, obj):
        queryset = IngredientRecipe.objects.filter(
            recipe=obj
        )
        return IngredientInRecipeSerializer(
            queryset,
            many=True
        ).data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return FavoriteRecipe.objects.filter(
            user=request.user,
            recipe=obj
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=request.user, recipe=obj).exists()


class SubscribeRecipeSerializer(serializers.ModelSerializer):


    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор для подписок."""

    id = serializers.IntegerField(
        source='author.id')
    email = serializers.EmailField(
        source='author.email'
    )
    username = serializers.CharField(
        source='author.username'
    )
    first_name = serializers.CharField(
        source='author.first_name'
    )
    last_name = serializers.CharField(
        source='author.last_name'
    )
    recipes = serializers.SerializerMethodField()
    is_subscribed = serializers.BooleanField(
        read_only=True
    )
    recipes_count = serializers.IntegerField(
        read_only=True
    )

    class Meta:
        model = Follow
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name',
            'is_subscribed', 'recipes',
            'recipes_count',
        )

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = (
            obj.author.recipe.all()[:int(limit)] if limit
            else obj.author.recipe.all())
        return SubscribeRecipeSerializer(
            recipes,
            many=True).data