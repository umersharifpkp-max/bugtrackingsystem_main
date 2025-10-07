from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class UserType(models.TextChoices):
        MANAGER = 'manager', 'Manager'
        QA = 'qa', 'QA'
        DEVELOPER = 'developer', 'Developer'

    user_type = models.CharField(max_length=20, choices=UserType.choices)
    email = models.EmailField(unique=True)

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.username} ({self.user_type})"
