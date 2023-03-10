from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from .models import User, Follow
from recipes.models import Recipe


class CustomUserSerializer(UserSerializer):

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
        )


class SubscribeRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscribeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(
        source='author.id'
    )
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
        ).data