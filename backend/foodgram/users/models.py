from enum import Enum

from django.contrib.auth.models import AbstractUser
from django.db import models
from foodgram.settings import (CHARFIELD_MAX_LENGTH, EMAIL_MAX_LENGTH,
                               USERNAME_MAX_LENGTH)

from .validators import validate_username


class Roles(Enum):
    user = 'user'
    blocked = 'blocked'
    admin = 'admin'

    @classmethod
    def get_roles(cls):
        return tuple((attribute.name, attribute.value) for attribute in cls)


class User(AbstractUser):
    username = models.CharField(
        verbose_name='Имя пользователя',
        validators=(validate_username,),
        max_length=USERNAME_MAX_LENGTH,
        unique=True,
        blank=False,
        null=False,
    )
    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        max_length=EMAIL_MAX_LENGTH,
        unique=True,
    )
    role = models.CharField(
        verbose_name='Роль',
        choices=Roles.get_roles(),
        default=Roles.user.value,
        max_length=CHARFIELD_MAX_LENGTH,
        blank=True
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=CHARFIELD_MAX_LENGTH,
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=CHARFIELD_MAX_LENGTH,
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    @property
    def is_admin(self):
        return self.role == Roles.admin.value

    @property
    def is_blocked(self):
        return self.role == Roles.blocked.value

    def __str__(self) -> str:
        return self.username


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Пользователь',
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ('following',)
        constraints = [
            models.UniqueConstraint(
                name="user_follow_unique_relationships",
                fields=["user", "following"],
            ),
            models.CheckConstraint(
                name="users_follow_not_self_follow",
                check=~models.Q(user=models.F("following")),
            )
        ]
