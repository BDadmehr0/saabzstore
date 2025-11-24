from django.db import models
from PIL import Image
import os

def product_image_path(instance, filename):
    ext = filename.split('.')[-1]  # امتداد فایل
    filename = f"{instance.id}.{ext}"  # نام‌گذاری بر اساس ID محصول
    return os.path.join("products", filename)


class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to=product_image_path, blank=True, null=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # آیا محصول قبلاً وجود داشته؟
        old_image = None
        if self.pk:
            try:
                old_image = Product.objects.get(pk=self.pk).image
            except Product.DoesNotExist:
                pass

        # ذخیره اولیه برای داشتن ID
        super().save(*args, **kwargs)

        # اگر عکس جدید آپلود شده و عکس قبلی وجود دارد → پاک شود
        if old_image and old_image != self.image:
            if os.path.isfile(old_image.path):
                os.remove(old_image.path)

        # اگر عکس ندارد، ادامه نده
        if not self.image:
            return

        # مسیر عکس جدید
        img_path = self.image.path
        img = Image.open(img_path)

        # Resize
        max_width = 800
        if img.width > max_width:
            ratio = max_width / float(img.width)
            new_height = int(float(img.height) * ratio)
            img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)

        # ذخیره مجدد عکس
        img.save(img_path)




class Order(models.Model):
    customer_name = models.CharField(max_length=200)
    email = models.EmailField()
    address = models.TextField()
    phone = models.CharField(max_length=20)
    products = models.ManyToManyField(Product)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, default='pending')

    def __str__(self):
        return f"Order {self.id} - {self.customer_name}"
