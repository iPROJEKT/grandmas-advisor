from rest_framework import generics, status, viewsets
from rest_framework.mixins import ListModelMixin, CreateModelMixin
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models.aggregates import Sum
from django.http import HttpResponse
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from django.db.models.aggregates import Count, Sum
from django.db.models.expressions import Exists, OuterRef, Value
from rest_framework.permissions import AllowAny
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

from .filters import  RecipeFilter
from .pagination import PaginationClass
from .serializers import (
    FavoriteSerializer, IngredientSerializer,
    RecipeListSerializer,
    ShoppingCartSerializer, TagSerializer,
    RecipeWriteSerializer
)
from .permissions import (
    AdminOrReadOnly,
    AuthorOrAdminOrReadOnly,
)
from recipes.models import  (
    Tag, Ingredients,
    Recipe, FavoriteRecipe,
    ShoppingCart, IngredientRecipe
)
from user.serializers import SubscribeRecipeSerializer

class GetObjectMixin:
    serializer_class = SubscribeRecipeSerializer
    permission_classes = (AllowAny,)

    def get_object(self):
        recipe_id = self.kwargs['recipe_id']
        recipe = get_object_or_404(Recipe, id=recipe_id)
        self.check_object_permissions(self.request, recipe)
        return recipe


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
    filterset_class = RecipeFilter
    filter_backends = [DjangoFilterBackend, ]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return RecipeWriteSerializer
        return RecipeListSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class AddDeleteFavoriteRecipe(
    GetObjectMixin,
    generics.RetrieveDestroyAPIView,
    generics.ListCreateAPIView
):
    def create(self, request, *args, **kwargs):
        instance = self.get_object()
        request.user.favorite_recipe.recipe.add(instance)
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_destroy(self, instance):
        self.request.user.favorite_recipe.recipe.remove(instance)


class AddDeleteShoppingCart(
    GetObjectMixin,
    generics.RetrieveDestroyAPIView,
    generics.ListCreateAPIView
):
    def create(self, request, *args, **kwargs):
        request.user.shopping_cart.recipe.add(self.get_object())
        serializer = self.get_serializer(self.get_object())
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_destroy(self, instance):
        self.request.user.shopping_cart.recipe.remove(instance)


@api_view(['GET'])
def download_shopping_cart(request):
    ingredient_list = "Cписок покупок:"
    ingredients = IngredientRecipe.objects.filter(
        recipe__shopping_cart__user=request.user
    ).order_by('ingredient__name').values(
        'ingredient__name', 'ingredient__measurement_unit'
    ).annotate(amount=Sum('amount'))
    for ingredient in ingredients:
        ingredient_list += (
            f"\n{ingredient['ingredient__name']} "
            f"({ingredient['ingredient__measurement_unit']}) - "
            f"{ingredient['amount']}"
        )
    file = 'shopping_list'
    response = HttpResponse(ingredient_list, 'Content-Type: application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{file}.txt"'
    return response