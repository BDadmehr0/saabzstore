# store/models.py
import os

from django.db import models
from PIL import Image


def product_image_path(instance, filename):
    ext = filename.split(".")[-1]
    # اگر id هنوز تعیین نشده باشد، Django یک نام موقت می‌سازد؛ ما بعد از save با نام جدید جایگزین می‌کنیم
    filename = f"{instance.id or 'temp'}.{ext}"
    return os.path.join("products", filename)


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)

    class Meta:
        verbose_name_plural = "دسته‌بندی‌ها"

    def __str__(self):
        return self.name


class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)

    class Meta:
        verbose_name_plural = "برند ها"

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200)
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
    inventory = models.PositiveIntegerField(default=0)  # موجودی برای فیلتر "فقط موجود"
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "محصولات"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # نگه داشتن تصویر قبلی برای حذف اگر آپدیت شد
        old_image = None
        if self.pk:
            try:
                old_image = Product.objects.get(pk=self.pk).image
            except Product.DoesNotExist:
                pass

        # ذخیره اولیه برای گرفتن ID (اگر ID نداشت)
        super().save(*args, **kwargs)

        # اگر عکس قبلی وجود داشت و با عکس جدید فرق می‌کرد حذفش کن
        if old_image and old_image != self.image:
            try:
                if old_image.path and os.path.isfile(old_image.path):
                    os.remove(old_image.path)
            except Exception:
                pass

        # اگر هیچ عکسی نیست، تمام
        if not self.image:
            return

        # اطمینان از نام‌گذاری بر اساس ID (در صورت استفاده از نام temp در upload_to)
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

        # ذخیره مجدد عکس
        try:
            img.save(img_path)
        except Exception:
            pass


class Order(models.Model):
    customer_name = models.CharField(max_length=200)
    email = models.EmailField()
    address = models.TextField()
    phone = models.CharField(max_length=20)
    products = models.ManyToManyField(Product)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, default="pending")

    class Meta:
        verbose_name_plural = "سفارش ها"

    def __str__(self):
        return f"Order {self.id} - {self.customer_name}"
