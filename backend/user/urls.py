from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import FollowViewSet


router = DefaultRouter()

router.register('subscriptions', FollowViewSet, basename='follow')

urlpatterns = [
    path('users/<int:user_id>/subscribe/',
        FollowViewSet, name='subscribe'
    ),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
