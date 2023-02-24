from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, filters
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.mixins import ListModelMixin, CreateModelMixin

from .permissions import AdminOrReadOnly
from .models import Tag, Ingredients, Recipe
from .serealizer import TagSerializer, IngridientSerealizator


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all().order_by('name')
    permission_classes = (AdminOrReadOnly,)
    serializer_class = TagSerializer


class IngredientsViewSet(viewsets.ModelViewSet):
    queryset = Ingredients.objects.all().order_by('name')
    serializer_class = IngridientSerealizator
    permission_classes = (AdminOrReadOnly,)
