from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


class User(AbstractUser):
    email = models.EmailField(
        max_length=settings.NAME_MAX_LENGTH,
        unique=True,
    )
    first_name = models.CharField(
        max_length=settings.USERNAME_MAX_LENGTH
    )
    last_name = models.CharField(
        max_length=settings.USERNAME_MAX_LENGTH
    )
    username = models.CharField(
        max_length=settings.USERNAME_MAX_LENGTH,
        unique=True,
    )

    def __str__(self):
        return self.username


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        related_name='follower',
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        User,
        related_name='following',
        on_delete=models.CASCADE,
    )
    created = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ('-author',)
        verbose_name = 'Лента автора'
        verbose_name_plural = 'Лента авторов'
        constraints = [
            models.CheckConstraint(
                name="prevent_self_follow",
                check=~models.Q(user=models.F("author")),
            ),
        ]
