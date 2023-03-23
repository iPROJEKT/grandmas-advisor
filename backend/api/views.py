from rest_framework import generics, status, viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models.aggregates import Sum
from django.http import HttpResponse
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.permissions import(
    IsAuthenticatedOrReadOnly,
)
from rest_framework.views import APIView

from user.models import User, Follow
from .filters import  AuthorAndTagFilter
from .pagination import PaginationClass
from .serializers import (
    IngredientSerializer,
    RecipeReadSerializer,
    TagSerializer,
    RecipeWriteSerializer,
    ShortRecipeSerializer,
    FavouriteSerializer,
    ShoppingCardSerializer,
    ShowFollowSerializer
)
from .permissions import (
    AdminOrReadOnly,
)
from recipes.models import  (
    Tag, Ingredients,
    Recipe, FavoriteRecipe,
    ShoppingCart, IngredientRecipe
)

def download_file_response(ingredients_list):
    buy_list = []
    for item in ingredients_list:
        buy_list.append(f'{item["ingredient__name"]} - {item["amount"]} '
                        f'{item["ingredient__measurement_unit"]} \n')

    response = HttpResponse(buy_list, 'Content-Type: text/plain')
    response['Content-Disposition'] = ('attachment; '
                                       'filename="buylist.txt"')
    return response


class GetObjectMixin(
    generics.RetrieveDestroyAPIView,
    generics.ListCreateAPIView,
):
    serializer_class = ShortRecipeSerializer
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
    queryset = Recipe.objects.all()
    filterset_class = AuthorAndTagFilter
    pagination_class = PaginationClass
    filter_backends = [DjangoFilterBackend, ]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class AddDeleteFavoriteRecipe(
    GetObjectMixin,
    generics.RetrieveDestroyAPIView,
    generics.ListCreateAPIView
):
    serializer_class = FavouriteSerializer
    pagination_class = PaginationClass
    filterset_class = AuthorAndTagFilter

    def get_recipe(self, obj): 
        recipes = get_object_or_404(Recipe, pk=obj.pk) 
        recipe = Recipe.objects.filter(recipe=recipes)
        return ShortRecipeSerializer(
            recipe,
            many=True
        ).data

    def create(self, request, *args, **kwargs):
        shop_card = FavoriteRecipe.objects.create(
            user=request.user,
            recipe=self.get_object()
        )
        serializer = FavouriteSerializer(
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
    GetObjectMixin,
    generics.RetrieveDestroyAPIView,
    generics.ListCreateAPIView,
):
    filterset_class = AuthorAndTagFilter
    serializer_class = ShoppingCardSerializer
    pagination_class = PaginationClass
    def create(self, request, *args, **kwargs):
        shop_card = ShoppingCart.objects.create(
            user=request.user,
            recipe=self.get_object()
        )
        serializer = ShoppingCardSerializer(
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


class FollowApiView(APIView):
    permission_classes = [permissions.IsAuthenticated, ]
    pagination_class = PaginationClass

    def post(self, request, *args, **kwargs):
        if Follow.objects.filter(
            author=get_object_or_404(
                User, pk=kwargs.get('id', None)
            ),
            user=request.user
        ).exists():
            return Response(
                {'errors': 'Вы уже подписаны на этого пользователя'},
                status=status.HTTP_400_BAD_REQUEST
            )
        obj_follow = Follow(author=get_object_or_404(
                User,
                pk=kwargs.get('id', None)
            ),
            user=request.user
        )
        obj_follow.save()
        serializer = ShowFollowSerializer(
            get_object_or_404(
                User, pk=kwargs.get('id', None)
            ),
            context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)
        subscription = get_object_or_404(
            Follow,
            user=user,
            author=author
        )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ListFollowViewSet(generics.ListAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated, ]
    serializer_class = ShowFollowSerializer
    pagination_class = PaginationClass

    def get_queryset(self):
        user = self.request.user
        return User.objects.filter(following__user=user)


@api_view(['GET'])
def download_shopping_cart(request):
    """Скачать список покупок."""
    ingredient_list = "Cписок покупок:"
    ingredients = IngredientRecipe.objects.filter(
        recipe__shopping_cart__user=request.user
    ).values(
        'ingredient__name',
        'ingredient__measurement_unit'
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
