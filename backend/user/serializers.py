from djoser.serializers import UserCreateSerializer, UserSerializer

from .models import User

class CustomUserSerializer(UserSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
        )


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = (
            "email",
            "username",
            "password",
        )