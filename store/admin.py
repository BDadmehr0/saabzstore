from django.contrib import admin

from .models import Brand, Category, Order, Product, ProductReview


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
    list_display = (
        "name",
        "brand",
        "category",
        "price",
        "inventory",
        "is_special",
        "created_at",
    )
    list_filter = ("brand", "category", "is_special")
    search_fields = ("name", "description")


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ("product", "user", "rating", "created_at")
    list_filter = ("rating", "created_at", "product")
    search_fields = ("user__username", "user__email", "product__name", "comment")
    ordering = ("-created_at",)


admin.site.register(Order)
