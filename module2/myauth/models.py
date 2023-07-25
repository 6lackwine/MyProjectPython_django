from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE) # Укажем связь с user 1 к 1. on_delete=models.CASCADE означает, что если user будет удален, то и профиль будет удален
    # Теперь укажем дополнительные поля
    bio = models.TextField(max_length=500, blank=True) # blank=True - позволяет хранить пустые значения
    agreement_accepted = models.BooleanField(default=False) # Позволит хранить информацию о том, что пользователь принял соглашение
