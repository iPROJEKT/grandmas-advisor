from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from djoser.serializers import UserCreateSerializer, UserSerializer
from django.shortcuts import get_object_or_404

from user.models import User, Follow
from recipes.models import Recipe

from recipes.models import (
    FavoriteRecipe,
    IngredientRecipe,
    Ingredients,
    Recipe,
    ShoppingCart, Tag
)
from user.models import User


class UserLimitParamsSerializer(UserSerializer):

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
        )


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = (
            'email',
            'username',
            'password',
            'first_name',
            'last_name',
        )


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = '__all__',


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredients
        fields = '__all__'
        read_only_fields = '__all__',


class IngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeReadSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserLimitParamsSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField(read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = '__all__'

    def get_ingredients(self, obj):
        return IngredientAmountSerializer(
            IngredientRecipe.objects.select_related(
                'ingredient'
            ).filter(
                recipe=obj,
            ),
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
            user=request.user,
            recipe=obj
        ).exists()


class IngredientsEditSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = Ingredients
        fields = ('id', 'amount')


class RecipeWriteSerializer(serializers.ModelSerializer):
    image = Base64ImageField(
        max_length=None,
        use_url=True
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    ingredients = IngredientsEditSerializer(
        many=True
    )

    class Meta:
        model = Recipe
        fields = '__all__'
        read_only_fields = ('author',)


    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise serializers.ValidationError(
                'Рецепт не может быть без ингредиентов'
            )
        for ingredient in ingredients:
            if int(ingredient.get('amount')) < 1:
                raise serializers.ValidationError(
                    'Добавьте все ингредиенты в рецепт'
                )
        return ingredients

    def create_ingredients(self, ingredients, recipe):
        for ingredient in ingredients:
            IngredientRecipe.objects.create(
                recipe=recipe,
                ingredient_id=ingredient.get('id'),
                amount=ingredient.get('amount'),
            )

    def create(self, validated_data):
        ingredient = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(ingredient, recipe)
        return recipe

    def update(self, instance, validated_data):
        if 'ingredients' in validated_data:
            ingredients = validated_data.pop('ingredients')
            ing = IngredientRecipe.objects.filter(
                recipe=instance,
            )
            ing.delete()
            self.create_ingredients(ingredients, instance)
        if 'tags' in validated_data:
            instance.tags.set(
                validated_data.pop('tags')
            )
        return super().update(
            instance,
            validated_data
        )

    def to_representation(self, instance):
        return RecipeReadSerializer(
            instance,
            context={
                'request': self.context.get('request')
            }
        ).data


class ShortRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FavouriteSerializer(serializers.ModelSerializer):
    recipe = serializers.SerializerMethodField()
    user = serializers.CharField()

    class Meta:
        model = FavoriteRecipe
        fields = '__all__'
 
    def get_recipe(self, obj, request): 
        return ShoppingCart.objects.filter(
            user=request.user,
            recipe=obj
        ).exists()
 
    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return ShortRecipeSerializer(
            instance.recipe,
            context=context
        ).data


class ShoppingCardSerializer(serializers.ModelSerializer):
    recipe = serializers.SerializerMethodField()
    user = serializers.CharField()

    class Meta:
        model = ShoppingCart
        fields = '__all__'
 
    def get_recipe(self, obj): 
        user = get_object_or_404(User, pk=obj.pk) 
        recipe = FavoriteRecipe.objects.filter(recipe=user)
        return ShortRecipeSerializer(
            recipe,
            many=True
        ).data
 
    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return ShortRecipeSerializer(
            instance.recipe,
            context=context
        ).data
    


class FollowingRecipesSerializers(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class ShowFollowSerializer(serializers.ModelSerializer): 
    is_subscribed = serializers.SerializerMethodField() 
    recipes = serializers.SerializerMethodField() 
    recipes_count = serializers.SerializerMethodField() 
 
    class Meta: 
        model = User 
        fields = ( 
            'id', 'email', 'username', 'first_name', 'last_name', 
            'is_subscribed', 'recipes', 'recipes_count' 
        ) 
        read_only_fields = fields 
 
    def get_is_subscribed(self, obj): 
        if not self.context['request'].user.is_authenticated: 
            return False 
        return Follow.objects.filter( 
            author=obj, user=self.context['request'].user).exists() 
 
    def get_recipes(self, obj): 
        user = get_object_or_404(User, pk=obj.pk) 
        recipes = Recipe.objects.filter(author=user) 
        return FollowingRecipesSerializers(recipes, many=True).data 
 
    def get_recipes_count(self, obj): 
        user = get_object_or_404(User, pk=obj.pk) 





