from django.urls import include, path

from user.views import FollowApiView, ListFollowViewSet

app_name = 'users'

urlpatterns = [
    path('users/<int:id>/subscribe/',
        FollowApiView.as_view(),
        name='subscribe'
    ),
    path('users/subscriptions/',
        ListFollowViewSet.as_view(),
        name='subscription'
    ),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
