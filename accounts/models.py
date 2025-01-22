from django.db import models
from django.contrib.auth.models import User
from random import randint

# Create your models here.

class TokenModel(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='کاربر')
    otp = models.CharField(verbose_name='رمز یکبارمصرف', max_length=6)
    status = models.CharField(verbose_name="وضعیت", max_length=100, null=True, blank=True)
    created_date = models.DateTimeField(verbose_name='تاریخ ایجاد', auto_now_add=True)
    modified_date = models.DateTimeField(verbose_name='تاریخ ویرایش', auto_now=True)

    def generate(self):
        v = randint(100000, 999999)
        self.otp = v
        return self.otp

    def __str__(self):
        return f"{self.user.username}"
    
    class Meta:
        verbose_name = 'رمز یکبارمصرف'
        verbose_name_plural = 'رمزهای یکبارمصرف'


class MobileModel(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='کاربر')
    mobile = models.CharField(verbose_name='شماره موبایل', max_length=11)
    created_date = models.DateTimeField(verbose_name='تاریخ ایجاد', auto_now_add=True)
    modified_date = models.DateTimeField(verbose_name='تاریخ ویرایش', auto_now=True)

    def __str__(self):
        return f"{self.mobile}"
    
    class Meta:
        verbose_name = 'موبایل کاربر'
        verbose_name_plural = 'موبایل کاربران'