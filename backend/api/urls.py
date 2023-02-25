from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import TagViewSet, IngredientsViewSet, ResipeViewSet, FavoriteViewSet


router = DefaultRouter()

router.register('tags', TagViewSet)
router.register('ingredients', IngredientsViewSet)
router.register('recipes', ResipeViewSet)
router.register(
    'recipes/<int:recipe_id>/favorite', FavoriteViewSet,
),


urlpatterns = [
    path('', include(router.urls)),
]
