from django.urls import include, path

from user.views import FollowViewSet

app_name = 'users'

urlpatterns = [
    path('users/<int:user_id>/subscribe/',
        FollowViewSet,
        name='subscribe'
    ),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
