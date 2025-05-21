from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

username_validator = RegexValidator(
    regex=r"^[\w.@+-]+$",
    message="Имя содержит недопустимые символы.",
)


class User(AbstractUser):
    email = models.EmailField(
        verbose_name="Адрес электронной почты",
        max_length=254,
        unique=True,
        help_text="Укажите ваш адрес электронной почты.",
    )
    username = models.CharField(
        verbose_name="Уникальный юзернейм",
        max_length=150,
        unique=True,
        help_text=(
            "Укажите ваш юзернейм (никнейм). Допустимые символы: "
            "буквы, цифры и @/./+/-/_"
        ),
        validators=[username_validator],
        error_messages={
            "unique": "Пользователь с таким юзернеймом уже существует.",
        },
    )
    first_name = models.CharField(
        verbose_name="Имя", max_length=150, help_text="Укажите ваше имя."
    )
    last_name = models.CharField(
        verbose_name="Фамилия", max_length=150,
        help_text="Укажите вашу фамилию."
    )
    avatar = models.ImageField(
        verbose_name="Аватар",
        upload_to="users/avatars/",
        blank=True,
        null=True,
        help_text="Загрузите ваш аватар",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    class Meta:
        ordering = ["username"]
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username


class UserSubscription(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="follower",
        verbose_name="Подписчик",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="following",
        verbose_name="Автор",
    )
    created = models.DateTimeField(verbose_name="Дата подписки",
                                   auto_now_add=True)

    class Meta:
        ordering = ["-created"]
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "author"],
                name="unique_user_author_subscription"
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F("author")),
                name="prevent_self_subscription",
            ),
        ]

    def __str__(self):
        return f"{self.user} подписан на {self.author}"
