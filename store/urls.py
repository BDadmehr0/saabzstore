# store/urls.py
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("product/<int:id>/<str:slug>/", views.product_detail, name="product_detail"),
    path("cart/", views.cart, name="cart"),
    path("checkout/", views.checkout, name="checkout"),
    path("store/", views.store, name="store"),
    path("category/<str:slug>/", views.category_view, name="category"),
    path("brand/<str:slug>/", views.brand_view, name="brand"),
    # API endpoint AJAX
    path("api/products/", views.api_products, name="api_products"),
    path(
        "api/product/<int:product_id>/add-review/",
        views.api_add_review,
        name="api_add_review",
    ),
    path(
        "api/product/<int:product_id>/reviews/",
        views.api_get_reviews,
        name="api_get_reviews",
    ),
    path(
        "api/review/<int:review_id>/delete/",
        views.api_delete_review,
        name="api_delete_review",
    ),
]
