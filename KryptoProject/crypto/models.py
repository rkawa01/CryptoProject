from django.db import models

class UserData(models.Model):
    wallet_dollars = models.IntegerField(default = 1000)
    wallet_bit = models.IntegerField(default = 0)

    def __str__(self):
        return "UserData"


class User(models.Model):
    user_data = models.ForeignKey(UserData, on_delete=models.CASCADE)
    login_field = models.CharField(max_length=50,unique=True)
    email_field = models.EmailField(max_length=254,unique=True)
    password_field = models.CharField(max_length=50)

    def __str__(self):
        return self.email_field




# Create your models here.
