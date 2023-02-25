from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, filters
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.mixins import ListModelMixin, CreateModelMixin

from .permissions import AdminOrReadOnly
from .models import Tag, Ingredients, Recipe
from .serealizer import TagSerializer, IngridientSerealizator, RecipeSerealizator, FollowSerializer


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all().order_by('name')
    serializer_class = TagSerializer
    permission_classes = (AdminOrReadOnly,)


class IngredientsViewSet(viewsets.ModelViewSet):
    queryset = Ingredients.objects.all().order_by('name')
    serializer_class = IngridientSerealizator
    permission_classes = (AdminOrReadOnly,)


class ResipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.select_related(
        'recipes', 'ingredients',
    )
    serializer_class = RecipeSerealizator


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
