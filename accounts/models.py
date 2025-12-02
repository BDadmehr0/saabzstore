import random
from datetime import timedelta

from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class MyUserManager(BaseUserManager):
    def create_user(
        self, phone_number=None, password=None, username=None, **extra_fields
    ):
        if not phone_number and not username:
            raise ValueError("کاربر باید یا شماره موبایل یا username داشته باشد")

        user = self.model(phone_number=phone_number, username=username, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password, **extra_fields):
        user = self.create_user(username=username, password=password, **extra_fields)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
    username = models.CharField(
        max_length=150, unique=True, null=True, blank=True
    )  # مخصوص admin
    name = models.CharField(max_length=50, default="کاربر پاپل")
    # تصویر پیش‌فرض برای همه کاربران
    profile_image = models.ImageField(
        upload_to="profile_image/",
        blank=True,
        null=True,
        default="default_profile_images.svg",
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = MyUserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.phone_number if self.phone_number else self.username


class OTP(models.Model):
    phone_number = models.CharField(max_length=15)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        return timezone.now() <= self.created_at + timedelta(
            minutes=5
        )  # OTP 5 دقیقه اعتبار دارد

    @staticmethod
    def generate_otp():
        return str(random.randint(100000, 999999))
