from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from .models import Tag

class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')

