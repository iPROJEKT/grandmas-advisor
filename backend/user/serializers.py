from djoser.serializers import UserSerializer
from rest_framework import serializers
from django.shortcuts import get_object_or_404

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
        recipes_limit = int(self.context['request'].GET.get(
            'recipes_limit', 10))
        user = get_object_or_404(User, pk=obj.pk)
        recipes = Recipe.objects.filter(author=user)[:recipes_limit]

        return FollowingRecipesSerializers(recipes, many=True).data

    def get_recipes_count(self, obj):
        user = get_object_or_404(User, pk=obj.pk)
        return Recipe.objects.filter(author=user).count()
