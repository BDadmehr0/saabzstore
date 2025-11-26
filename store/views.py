# store/views.py
from django.core.paginator import EmptyPage, Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.db.models import Count

from .models import Brand, Category, Product

import random

def index(request):
    special_products = list(Product.objects.filter(is_special=True))

    # اگر بیشتر از 3 تا بود → تصادفی ۳ تا انتخاب کن
    if len(special_products) > 3:
        special_products = random.sample(special_products, 3)

    context = {
        "special_products": special_products,
    }
    return render(request, "store/index.html", context)



def store(request):
    """
    صفحهٔ اصلی فروشگاه — قالب را رندر می‌کند.
    خود فیلتر و لود محصولات از طریق AJAX انجام می‌شود، ولی برای سئو و fallback
    می‌توانیم page اول را نیز از سرور رندر کنیم (اختیاری).
    """
    categories = Category.objects.all()
    brands = Brand.objects.all()
    # initial products برای نمایش سروری (صفحه 1)
    products_qs = Product.objects.all().order_by("-created_at")[:12]
    return render(
        request,
        "store/store.html",
        {
            "products": products_qs,
            "categories": categories,
            "brands": brands,
        },
    )


def product_detail(request, id, slug):
    """
    نمایش جزئیات یک محصول بر اساس id و slug
    """
    product = get_object_or_404(Product, id=id, slug=slug)

    # محصولات مرتبط
    related_products = (
        Product.objects.filter(category=product.category).exclude(id=product.id)[:6]
        if product.category
        else []
    )

    context = {
        "product": product,
        "related_products": related_products,
    }
    return render(request, "store/product_detail.html", context)


def cart(request):
    return render(request, "store/cart.html")


def checkout(request):
    return render(request, "store/checkout.html")


# ---------------------------
# API endpoint برای AJAX
# ---------------------------
def api_products(request):
    qs = Product.objects.all()

    # جستجو
    q = request.GET.get("q")
    if q:
        qs = qs.filter(name__icontains=q)

    # دسته‌بندی‌ها (multi-select) — می‌پذیرد: categories=1,2,3 یا categories=slug1,slug2
    categories = request.GET.get("categories")  # مثال: "1,2,3"
    if categories:
        cat_ids = [c for c in categories.split(",") if c.strip()]
        qs = qs.filter(category__id__in=cat_ids)

    # برندها (multi-select)
    brands = request.GET.get("brands")
    if brands:
        brand_ids = [b for b in brands.split(",") if b.strip()]
        qs = qs.filter(brand__id__in=brand_ids)

    # قیمت
    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")
    if min_price:
        try:
            qs = qs.filter(price__gte=float(min_price))
        except ValueError:
            pass
    if max_price:
        try:
            qs = qs.filter(price__lte=float(max_price))
        except ValueError:
            pass

    # فقط موجودها
    in_stock = request.GET.get("in_stock")
    if in_stock in ["1", "true", "True"]:
        qs = qs.filter(inventory__gte=1)

    # مرتب سازی
    sort = request.GET.get("sort")
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
    page = request.GET.get("page", 1)
    per_page = request.GET.get("per_page", 12)
    try:
        page = int(page)
    except ValueError:
        page = 1
    try:
        per_page = int(per_page)
    except ValueError:
        per_page = 12

    paginator = Paginator(qs, per_page)
    try:
        page_obj = paginator.page(page)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    products_data = []
    for product in page_obj.object_list:
        products_data.append(
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
        )

    data = {
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
    return JsonResponse(data)
