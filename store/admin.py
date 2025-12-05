from django.contrib import admin

from .models import (Brand, Cart, CartItem, Category, Order, Product,
                     ProductReview)


# ------------------ Category ------------------
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


# ------------------ Brand ------------------
@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


# ------------------ Product ------------------
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


# ------------------ ProductReview ------------------
@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ("product", "user", "rating", "created_at")
    list_filter = ("rating", "created_at", "product")
    search_fields = ("user__username", "user__email", "product__name", "comment")
    ordering = ("-created_at",)


# ------------------ CartItem Inline ------------------
class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ("item_display",)
    can_delete = False
    fields = ("item_display",)

    def item_display(self, obj):
        return f"{obj.product.name} x {obj.quantity}"

    item_display.short_description = "آیتم سبد خرید"


# ------------------ Cart Admin ------------------
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("user", "created_at")
    inlines = [CartItemInline]
    ordering = ("user__username",)


# ------------------ Order ------------------
admin.site.register(Order)
