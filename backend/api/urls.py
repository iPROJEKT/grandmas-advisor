from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (IngredientsViewSet,
    RecipesViewSet,
    TagViewSet,
    download_shopping_cart,
    AddDeleteFavoriteRecipe,
    AddDeleteShoppingCart
)

router = DefaultRouter()

router.register('recipes', RecipesViewSet, basename='recipes')
router.register('ingredients', IngredientsViewSet, basename='ingredients')
router.register('tags', TagViewSet, basename='tags')

urlpatterns = [
    path(
        'recipes/<int:recipe_id>/favorite/',
        AddDeleteFavoriteRecipe.as_view(),
        name='favorite_recipe'),
    path(
        'recipes/<int:recipe_id>/shopping_cart/',
        AddDeleteShoppingCart.as_view(),
        name='shopping_cart'),
    path(
        'recipes/download_shopping_cart/',
        download_shopping_cart,
        name='download_shopping_cart'
    ),
    path('', include(router.urls)),
]