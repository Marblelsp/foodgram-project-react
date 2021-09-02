from django.contrib.auth.models import AbstractUser
from django.db import models


class Type:
    USER = 'USER'
    ADMIN = 'ADMIN'
    ROLE = (
        ("USER", "USER"),
        ("ADMIN", "ADMIN"),
    )


class CustomUser(AbstractUser):
    role = models.CharField(
        max_length=20,
        choices=Type.ROLE,
        default=Type.USER,
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
        return self.role == Type.ADMIN or self.is_superuser
