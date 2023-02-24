from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


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
