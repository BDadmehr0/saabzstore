from django.contrib import admin

from .models import Brand, Category, Order, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "brand", "category", "price", "inventory", "is_special", "created_at")
    list_filter = ("brand", "category", "is_special")
    search_fields = ("name", "description")


admin.site.register(Order)
