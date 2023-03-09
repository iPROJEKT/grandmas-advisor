from rest_framework import viewsets
from rest_framework.mixins import ListModelMixin, CreateModelMixin
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models.aggregates import Sum
from django.http import HttpResponse
from rest_framework import viewsets, filters
from rest_framework.decorators import api_view
from rest_framework import viewsets, status
from django.shortcuts import get_object_or_404
from django.db.models.aggregates import Count, Sum
from django.db.models.expressions import Exists, OuterRef, Value
from rest_framework.permissions import(
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
    SAFE_METHODS
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework.response import Response
from rest_framework.decorators import api_view, action
from rest_framework.views import APIView

from .pagination import PaginationClass
from .serializers import (
    FavoriteSerializer, IngredientSerializer,
    RecipeListSerializer, RecipeSerializer,
    ShoppingCartSerializer, TagSerializer
)
from .permissions import (
    AdminOrReadOnly,
    AuthorOrAdminOrReadOnly
)
from recipes.models import  (
    Tag, Ingredients,
    Recipe, FavoriteRecipe,
    ShoppingCart, IngredientRecipe
)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all().order_by('name')
    serializer_class = TagSerializer
    permission_classes = (AdminOrReadOnly,)
    filter_backends = [DjangoFilterBackend, ]


class IngredientsViewSet(viewsets.ModelViewSet):
    queryset = Ingredients.objects.all().order_by('name')
    serializer_class = IngredientSerializer
    permission_classes = (AdminOrReadOnly,)
    filter_backends = [DjangoFilterBackend, ]


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all().order_by('name')
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = PaginationClass
    filter_backends = [DjangoFilterBackend, ]

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeSerializer
        return RecipeListSerializer
