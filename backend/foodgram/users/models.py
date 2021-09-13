from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUserRole(models.TextChoices):
    admin = 'admin', 'admin'
    user = 'user', 'user'
    moderator = 'moderator', 'moderator'


class CustomUser(AbstractUser):
    role = models.CharField(
        max_length=20,
        choices=CustomUserRole.choices,
        default=CustomUserRole.user,
    )
    email = models.EmailField(
        max_length=254, unique=True,
        blank=False, null=False
    )
    first_name = models.CharField(
        help_text='Укажите ваше имя',
        max_length=150
    )
    last_name = models.CharField(
        help_text='Укажите вашу фамилию',
        max_length=150
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', ]

    @property
    def is_admin(self):
        return self.role == CustomUserRole.admin or self.is_superuser


class Follow(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="followers"
    )
    following = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="following"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "following"],
                name="unique_author_user_following")
        ]
