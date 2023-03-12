from rest_framework import generics, status, viewsets
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models.aggregates import Sum
from django.http import HttpResponse
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.permissions import(
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
    SAFE_METHODS
)
from rest_framework.response import Response
from rest_framework.decorators import api_view

from .filters import  RecipeFilter
from .pagination import PaginationClass
from .serializers import (
    FavoriteSerializer, IngredientSerializer,
    RecipeReadSerializer,
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
from user.serializers import FollowingRecipesSerializers


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
        if self.request.method == 'GET':
            return RecipeReadSerializer
        return RecipeWriteSerializer


class AddDeleteFavoriteRecipe(
    generics.RetrieveDestroyAPIView,
    generics.ListCreateAPIView
):
    serializer_class = FavoriteSerializer
    permission_classes = (AllowAny,)

    def get_object(self):
        return get_object_or_404(Recipe, id=self.kwargs['recipe_id'])

    def create(self, request, *args, **kwargs):
        shop_card = FavoriteRecipe.objects.create(
            user=request.user,
            recipe=self.get_object()
        )
        serializer = FavoriteSerializer(
            shop_card,
            context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_destroy(self, instance):
        resipe_del = FavoriteRecipe.objects.filter(
            recipe=self.get_object()
        )
        resipe_del.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AddDeleteShoppingCart(
    generics.RetrieveDestroyAPIView,
    generics.ListCreateAPIView,
):
    serializer_class = ShoppingCartSerializer
    permission_classes = (AllowAny,)

    def get_object(self):
        recipe = get_object_or_404(Recipe, id=self.kwargs['recipe_id'])
        self.check_object_permissions(self.request, recipe)
        return recipe

    def post(self, request, *args, **kwargs):
        shop_card = ShoppingCart.objects.create(
            user=request.user,
            recipe=self.get_object()
        )
        serializer = ShoppingCartSerializer(
            shop_card,
            context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_destroy(self, instance):
        resipe_del = ShoppingCart.objects.filter(
            recipe=self.get_object()
        )
        resipe_del.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


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
