from enum import Enum

from django.contrib.auth.models import AbstractUser
from django.db import models

from foodgram.settings import (
    CHARFIELD_MAX_LENGTH, EMAIL_MAX_LENGTH, USERNAME_MAX_LENGTH
)
from validators import validate_username


class Roles(Enum):
    user = 'user'
    moderator = 'moderator'
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
        blank=True
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=CHARFIELD_MAX_LENGTH,
        blank=True
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=CHARFIELD_MAX_LENGTH,
        blank=True
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    @property
    def is_admin(self):
        return self.role == Roles.admin.value

    @property
    def is_moderator(self):
        return self.role == Roles.moderator.value

    def __str__(self) -> str:
        return self.username


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Пользователь',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
        blank=True,
        null=True,
    )
