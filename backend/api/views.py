from rest_framework import viewsets
from rest_framework.mixins import ListModelMixin, CreateModelMixin
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models.aggregates import Sum
from django.http import HttpResponse
from rest_framework import viewsets, filters
from rest_framework.decorators import api_view
from rest_framework import viewsets, status
from django.shortcuts import get_object_or_404
from rest_framework.permissions import(
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
    SAFE_METHODS
)
from rest_framework.response import Response
from rest_framework.decorators import api_view, action
from rest_framework.views import APIView

from .serializers import (
    TagSerializer,
    IngredientSerializer,
    FollowSerializer,
    CreateRecipeSerializer,
    FavoriteSerializer,
    ShoppingCartSerializer,
    ShowRecipeSerializer,
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


class IngredientsViewSet(viewsets.ModelViewSet):
    queryset = Ingredients.objects.all().order_by('name')
    serializer_class = IngredientSerializer
    permission_classes = (AdminOrReadOnly,)
    filter_backends = [DjangoFilterBackend, ]


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.select_related(
        'recipes', 'ingredients'
    ).order_by('recipes')
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        method = self.request.method
        if method == "POST" or method == "PATCH":
            return CreateRecipeSerializer
        return ShowRecipeSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context


class FavoriteView(APIView):
    permissions = [IsAuthenticatedOrReadOnly, ]

    @action(methods=['post',],detail=True,)
    def post(self, request, recipe_id):
        user = request.user
        data = {
            "user": user.id,
            "recipe": recipe_id,
        }
        if FavoriteRecipe.objects.filter(
            user=user, recipe__id=recipe_id
        ).exists():
            return Response(
                {"Ошибка": "Уже в избранном"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = FavoriteSerializer(
            data=data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(methods=['DELETE',],detail=True,)
    def delete(self, request, recipe_id):
        user = request.user
        recipe = get_object_or_404(Recipe, id=recipe_id)
        if not FavoriteRecipe.objects.filter(
            user=user, recipe=recipe
        ).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        FavoriteRecipe.objects.get(user=user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingCartViewSet(APIView):

    permission_classes = [IsAuthenticatedOrReadOnly, ]
    pagination_class = None

    @action(methods=['post'],detail=True)
    def post(self, request, recipe_id):
        user = request.user
        data = {
            "user": user.id,
            "recipe": recipe_id,
        }
        if ShoppingCart.objects.filter(
                user=user, recipe__id=recipe_id
        ).exists():
            return Response(
                {"Ошибка": "Уже есть в корзине"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = ShoppingCartSerializer(
            data=data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(method=['delete',], detail=True)
    def delete(self, request, recipe_id):
        user = request.user
        recipe = get_object_or_404(Recipe, id=recipe_id)
        if not ShoppingCart.objects.filter(
            user=user, recipe=recipe
        ).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        ShoppingCart.objects.get(user=user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FollowViewSet(
    CreateModelMixin,
    ListModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['=following__username', ]

    def get_queryset(self):
        user = self.request.user
        return user.follower.all().order_by(
            'user'
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@api_view(['GET'])
def download_shopping_cart(request):
    """Скачать список покупок."""
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
