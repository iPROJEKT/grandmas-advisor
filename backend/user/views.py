from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.pagination import PaginationClass
from .models import User, Follow
from .serializers import ShowFollowSerializer


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
