from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from djoser.serializers import UserSerializer

from user.serializers import CustomUserSerializer
from .models import Tag, Recipe, Ingredients
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
