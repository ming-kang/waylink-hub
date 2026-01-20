from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """扩展用户模型"""
    phone = models.CharField(max_length=11, unique=True, verbose_name='手机号')
    avatar = models.URLField(max_length=500, blank=True, null=True, verbose_name='头像')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='余额')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='注册时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username or self.phone
