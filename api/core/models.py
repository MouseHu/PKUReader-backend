from django.db import models
from django.contrib.auth.models import User
# Create your models here.
from django.contrib.auth.models import AbstractUser

class Word(models.Model):
    raw = models.CharField(max_length=50)
    meaning = models.TextField()
    def __str__(self):
        return self.raw

class UserProfile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE) # 关联自带的User结构
    glossary = models.ManyToManyField(Word) #生词表
    # 可以添加更多的资料

    def __str__(self):
        return self.user.__str__()