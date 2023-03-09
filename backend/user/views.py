from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, filters
from rest_framework.mixins import ListModelMixin, CreateModelMixin

from .models import User
from .serializers import FollowSerializer


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