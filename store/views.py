from django.shortcuts import render, get_object_or_404
from .models import Product

def index(request):
    products = Product.objects.all()
    return render(request, 'store/index.html', {'products': products})

def store(request):
    q = request.GET.get('q')
    
    if q:
        products = Product.objects.filter(name__icontains=q)
    else:
        products = Product.objects.all()

    return render(request, 'store/store.html', {
        'products': products,
        'query': q
    })


def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    return render(request, 'store/product_detail.html', {'product': product})

def cart(request):
    return render(request, 'store/cart.html')

def checkout(request):
    return render(request, 'store/checkout.html')
