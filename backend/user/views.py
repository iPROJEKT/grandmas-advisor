from django.db.models.aggregates import Count 
from django.db.models.expressions import Value
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response

from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, filters
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.mixins import ListModelMixin, CreateModelMixin

from .models import User
from .serializers import SubscribeSerializer


class FollowViewSet(
    CreateModelMixin,
    ListModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = SubscribeSerializer
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
