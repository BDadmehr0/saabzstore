# store/views.py
import json
import random

from django.core.paginator import EmptyPage, Paginator
from django.db.models import Avg, Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import Brand, Category, Order, Product, ProductReview


# ---------------------------
# صفحه اصلی (با محصولات ویژه)
# ---------------------------
def index(request):
    special_products = list(Product.objects.filter(is_special=True))

    # اگر بیشتر از ۳ تا محصول ویژه داریم → ۳ تا تصادفی نمایش بده
    if len(special_products) > 3:
        special_products = random.sample(special_products, 3)

    return render(request, "store/index.html", {"special_products": special_products})


# ---------------------------
# صفحه فروشگاه
# ---------------------------
def store(request):
    """
    صفحهٔ اصلی فروشگاه — قالب را رندر می‌کند.
    """
    categories = Category.objects.all()
    brands = Brand.objects.all()

    # گرفتن پارامتر سرچ
    q = request.GET.get("q", "").strip()
    products_qs = Product.objects.all()
    if q:
        products_qs = products_qs.filter(
            Q(name__icontains=q) | Q(description__icontains=q)
        )

    # مرتب‌سازی بر اساس جدیدترین
    products_qs = products_qs.order_by("-created_at")[:12]

    return render(
        request,
        "store/store.html",
        {
            "products": products_qs,
            "categories": categories,
            "brands": brands,
        },
    )


# ---------------------------
# جزئیات محصول
# ---------------------------
from django.shortcuts import get_object_or_404, redirect, render

from .models import Product, ProductSlugHistory


def product_detail(request, id, slug):
    # گرفتن محصول بر اساس id
    product = get_object_or_404(Product, id=id)

    # اگر slug تغییر کرده باشد → ریدایرکت 301 به slug جدید
    if product.slug != slug:
        return redirect(
            "product_detail", id=product.id, slug=product.slug, permanent=True
        )

    # نمایش محصولات مرتبط
    related_products = (
        Product.objects.filter(category=product.category).exclude(id=product.id)[:6]
        if product.category
        else []
    )

    return render(
        request,
        "store/product_detail.html",
        {
            "product": product,
            "related_products": related_products,
        },
    )


def cart(request):
    return render(request, "store/cart.html")


def checkout(request):
    return render(request, "store/checkout.html")


# ============================================================
# API محصولات — نسخه نهایی و درست‌شده
# ============================================================
from django.core.cache import cache


def api_products(request):
    qs = Product.objects.all()
    search = request.GET.get("q", "").strip()
    categories = request.GET.get("categories")
    brands = request.GET.get("brands")
    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")
    in_stock = request.GET.get("in_stock")
    sort = request.GET.get("sort")
    page = request.GET.get("page", 1)
    per_page = request.GET.get("per_page", 12)

    # کلید cache براساس پارامترها
    cache_key = f"products_{search}_{categories}_{brands}_{min_price}_{max_price}_{in_stock}_{sort}_{page}_{per_page}"
    cached_data = cache.get(cache_key)
    if cached_data:
        return JsonResponse(cached_data)

    # --- فیلترها همانطور که قبلا بود ---
    if search:
        qs = qs.filter(
            Q(name__icontains=search)
            | Q(description__icontains=search)
            | Q(brand__name__icontains=search)
            | Q(category__name__icontains=search)
            | Q(slug__icontains=search)
        )
    if categories:
        qs = qs.filter(category__id__in=[c for c in categories.split(",")])
    if brands:
        qs = qs.filter(brand__id__in=[b for b in brands.split(",")])
    if min_price:
        qs = qs.filter(price__gte=float(min_price))
    if max_price:
        qs = qs.filter(price__lte=float(max_price))
    if in_stock in ["1", "true", "True"]:
        qs = qs.filter(inventory__gte=1)
    if sort == "price_asc":
        qs = qs.order_by("price")
    elif sort == "price_desc":
        qs = qs.order_by("-price")
    elif sort == "newest":
        qs = qs.order_by("-created_at")
    elif sort == "oldest":
        qs = qs.order_by("created_at")
    else:
        qs = qs.order_by("-created_at")

    # صفحه‌بندی
    paginator = Paginator(qs, per_page)
    page_obj = paginator.get_page(page)
    products_data = [
        {
            "id": product.id,
            "name": product.name,
            "slug": product.slug,
            "description": product.description[:200],
            "price": str(product.price),
            "image": product.image.url if product.image else None,
            "category": product.category.name if product.category else None,
            "brand": product.brand.name if product.brand else None,
            "inventory": product.inventory,
        }
        for product in page_obj.object_list
    ]

    response_data = {
        "results": products_data,
        "pagination": {
            "page": page_obj.number,
            "per_page": per_page,
            "total_pages": paginator.num_pages,
            "total_items": paginator.count,
            "has_next": page_obj.has_next(),
            "has_prev": page_obj.has_previous(),
        },
    }

    cache.set(cache_key, response_data, 60 * 5)  # cache به مدت 5 دقیقه
    return JsonResponse(response_data)


@csrf_exempt
def api_add_review(request, product_id):
    if not request.user.is_authenticated:
        return JsonResponse({"success": False, "error": "ابتدا وارد شوید."})

    product = get_object_or_404(Product, id=product_id)

    # آیا کاربر این محصول را خریده؟
    has_bought = Order.objects.filter(
        phone=request.user.phone_number,
        products=product,
    ).exists()

    if not has_bought:
        return JsonResponse(
            {"success": False, "error": "شما این محصول را خریداری نکرده‌اید."}
        )

    data = json.loads(request.body)

    rating = int(data.get("rating", 5))
    comment = data.get("comment", "").strip()

    if rating < 1 or rating > 5:
        return JsonResponse({"success": False, "error": "امتیاز نامعتبر است."})

    # جلوگیری از ثبت چندباره
    review, created = ProductReview.objects.update_or_create(
        user=request.user,
        product=product,
        defaults={"rating": rating, "comment": comment},
    )

    return JsonResponse({"success": True, "message": "نظر با موفقیت ثبت شد."})


def api_get_reviews(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    reviews = product.reviews.all().order_by("-created_at")

    avg_rating = reviews.aggregate(avg=Avg("rating"))["avg"] or 0
    count = reviews.count()

    data = [
        {
            "id": r.id,
            "user": r.user.name,
            "rating": r.rating,
            "comment": r.comment,
            "created_at": r.created_at.strftime("%Y-%m-%d"),
            "can_delete": request.user.is_authenticated
            and (r.user == request.user or request.user.is_staff),
        }
        for r in reviews
    ]

    return JsonResponse(
        {"reviews": data, "avg_rating": round(avg_rating, 1), "count": count}
    )


@csrf_exempt
@require_POST
def api_delete_review(request, review_id):
    if not request.user.is_authenticated:
        return JsonResponse({"success": False, "error": "ابتدا وارد شوید."})

    try:
        review = ProductReview.objects.get(id=review_id)
    except ProductReview.DoesNotExist:
        return JsonResponse({"success": False, "error": "نظر پیدا نشد."})

    # فقط کاربر صاحب نظر یا ادمین می‌تواند حذف کند
    if review.user != request.user and not request.user.is_staff:
        return JsonResponse({"success": False, "error": "دسترسی ندارید."})

    review.delete()
    return JsonResponse({"success": True, "message": "نظر با موفقیت حذف شد."})


# ---------------------------
# نمایش دسته
# ---------------------------
def category_view(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category)

    return render(
        request,
        "store/category.html",
        {
            "category": category,
            "products": products,
        },
    )


# ---------------------------
# نمایش برند
# ---------------------------
def brand_view(request, slug):
    brand = get_object_or_404(Brand, slug=slug)
    products = Product.objects.filter(brand=brand)

    return render(
        request,
        "store/brand.html",
        {
            "brand": brand,
            "products": products,
        },
    )
