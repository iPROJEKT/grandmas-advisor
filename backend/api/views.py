from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse
from rest_framework import viewsets, filters, status
from rest_framework.views import APIView
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.mixins import ListModelMixin, CreateModelMixin
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import api_view, action
from rest_framework.response import Response


from .permissions import AdminOrReadOnly
from .models import Tag, Ingredients, Recipe, FavoriteRecipe, ShoppingCart, IngredientRecipe
from .serealizer import TagSerializer, IngridientSerealizator, RecipeSerealizator, FollowSerializer, FavoriteSerealizator, ShoppingCartSerializer


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all().order_by('name')
    serializer_class = TagSerializer
    permission_classes = (AdminOrReadOnly,)


class IngredientsViewSet(viewsets.ModelViewSet):
    queryset = Ingredients.objects.all().order_by('name')
    serializer_class = IngridientSerealizator
    permission_classes = (AdminOrReadOnly,)
    filter_backends = [DjangoFilterBackend, ]


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


class FavoriteView(APIView):
    permissions = [IsAuthenticatedOrReadOnly, ]

    @action(methods=['post',], detail=True,)
    def post(self, request, recipe_id):
        data = {
            "user": request.user.id,
            "recipe": recipe_id,
        }
        if FavoriteRecipe.objects.filter(
            user=request.user, recipe__id=recipe_id
        ).exists():
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = FavoriteSerealizator(
            data=data, context={
                'request': request
            }
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
    permission_classes = [IsAuthenticatedOrReadOnly,]

    @action(methods=['post'], detail=True,)
    def post(self, request, recipe_id):
        user = request.user
        data = {
            'user': user.id,
            'recipe': recipe_id,
        }
        if ShoppingCart.objects.filter(
            user=user, recipe__id=recipe_id
        ).exists():
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = ShoppingCartSerializer(
            data=data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


    @action(method=['delete',], detail=True)
    def delete(self, request, recipe_id):
        if not ShoppingCart.objects.filter(
            user=request.user, recipe=get_object_or_404(
                Recipe,
                id=recipe_id
            )
        ).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        ShoppingCart.objects.get(
            user=request.user,
            recipe=get_object_or_404(
                Recipe,
                id=recipe_id
            )
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET"])
def download_shopping_cart(request):
    shopping_cart = request.user.shopping_cart.all()
    buying_list = {}
    for record in shopping_cart:
        ingredients = IngredientRecipe.objects.filter(recipe=record.recipe)
        for ingredient in ingredients:
            if name not in buying_list:
                buying_list[name] = {
                    "measurement_unit": ingredient.ingredient.measurement_unit,
                    "amount": ingredient.amount,
                }
            else:
                buying_list[name]["amount"] = (
                    buying_list[name]["amount"] + ingredient.amount
                )
    wishlist = []
    for name, data in buying_list.items():
        wishlist.append(
            f"{name} - {data['amount']} {data['measurement_unit']}"
        )
    response = HttpResponse(wishlist, content_type="text/plain")
    return response