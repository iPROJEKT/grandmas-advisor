from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import TagViewSet, IngredientsViewSet


router = DefaultRouter()

router.register('tags', TagViewSet)
router.register('ingredients', IngredientsViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
