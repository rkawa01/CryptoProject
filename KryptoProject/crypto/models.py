from django.db import models
from django.contrib.auth.models import User as mainUser


class UserData(models.Model):
    username = models.CharField(max_length=50,unique=True)
    wallet_dollars = models.IntegerField(default = 1000)
    wallet_bit = models.IntegerField(default = 0)

    def __str__(self):
        return self.username


class User(models.Model):
    user = models.OneToOneField(mainUser, on_delete=models.CASCADE)
    user_data = models.OneToOneField(UserData, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username




# Create your models here.
