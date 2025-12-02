# store/models.py
import os
import re

from django.db import models
from django.utils.text import slugify
from PIL import Image


# -----------------------------
# مسیر ذخیره تصویر محصول
# -----------------------------
def product_image_path(instance, filename):
    ext = filename.split(".")[-1]
    filename = f"{instance.id or 'temp'}.{ext}"
    return os.path.join("products", filename)


# -----------------------------
# Helper برای ساخت slug
# -----------------------------
def clean_slug(name):
    slug = slugify(name, allow_unicode=True)
    slug = re.sub(r"[^\w\-]", "", slug)  # فقط حروف، اعداد، _ و - باقی می‌ماند
    slug = re.sub(r"[-]+", "-", slug)  # جلوگیری از چند خط فاصله پشت سر هم
    return slug.strip("-")


# -----------------------------
# مدل دسته‌بندی
# -----------------------------
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True, allow_unicode=True)

    class Meta:
        verbose_name_plural = "دسته‌بندی‌ها"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = clean_slug(self.name)
            slug = base_slug
            counter = 1
            while Category.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


# -----------------------------
# مدل برند
# -----------------------------
class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True, allow_unicode=True)

    class Meta:
        verbose_name = "برند"
        verbose_name_plural = "برندها"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = clean_slug(self.name)
            slug = base_slug
            counter = 1
            while Brand.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


# -----------------------------
# تاریخچه Slug محصولات
# -----------------------------
class ProductSlugHistory(models.Model):
    product = models.ForeignKey(
        "Product", on_delete=models.CASCADE, related_name="slug_history"
    )
    old_slug = models.SlugField(max_length=220, allow_unicode=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.old_slug} -> {self.product.name}"


# -----------------------------
# مدل محصول
# -----------------------------
class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True, allow_unicode=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=0)
    image = models.ImageField(upload_to=product_image_path, blank=True, null=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
    )
    brand = models.ForeignKey(
        Brand, on_delete=models.SET_NULL, null=True, blank=True, related_name="products"
    )
    inventory = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    is_special = models.BooleanField(default=False, verbose_name="محصول ویژه")

    class Meta:
        verbose_name_plural = "محصولات"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # ذخیره slug قدیمی قبل از تغییر
        if self.pk:
            old = Product.objects.get(pk=self.pk)
            if old.slug != self.slug and self.slug:  # اگر slug جدید تنظیم شده
                ProductSlugHistory.objects.create(product=self, old_slug=old.slug)

        # ساخت slug خودکار اگر خالی باشد
        if not self.slug:
            base_slug = clean_slug(self.name)
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug

        # ذخیره اولیه برای گرفتن ID
        old_image = None
        if self.pk:
            try:
                old_image = Product.objects.get(pk=self.pk).image
            except Product.DoesNotExist:
                pass

        super().save(*args, **kwargs)

        # حذف عکس قبلی در صورت آپدیت
        if old_image and old_image != self.image:
            try:
                if old_image.path and os.path.isfile(old_image.path):
                    os.remove(old_image.path)
            except Exception:
                pass

        if not self.image:
            return

        # تغییر اندازه تصویر
        img_path = self.image.path
        try:
            img = Image.open(img_path)
        except Exception:
            return

        max_width = 800
        if img.width > max_width:
            ratio = max_width / float(img.width)
            new_height = int(float(img.height) * ratio)
            img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)

        try:
            img.save(img_path)
        except Exception:
            pass


from django.contrib.auth import get_user_model

User = get_user_model()


class ProductReview(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="reviews"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(default=5)  # 1–5
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("product", "user")  # هر کاربر فقط یک بار نظر بدهد

    def __str__(self):
        return f"{self.user.name} - {self.product.name} ({self.rating})"


# -----------------------------
# مدل سفارش
# -----------------------------
class Order(models.Model):
    customer_name = models.CharField(max_length=200)
    email = models.EmailField()
    address = models.TextField()
    phone = models.CharField(max_length=20)
    products = models.ManyToManyField(Product)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "سفارش ها"

    def __str__(self):
        return f"Order {self.id} - {self.customer_name}"


# -----------------------------
# مدل Variant
# -----------------------------
class Variant(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="variants"
    )
    name = models.CharField(max_length=120)
    price = models.PositiveIntegerField()
    inventory = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.product.name} - {self.name}"


# -----------------------------
# مدل Specification
# -----------------------------
class Specification(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="specifications"
    )
    name = models.CharField(max_length=120)
    value = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name}: {self.value}"
