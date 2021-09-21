from django.shortcuts import get_object_or_404, render
from shop.models import *

# Create your views here.
from django.http import HttpResponse

def index(request):
    # return HttpResponse("Hello Magic")
    products = Product.objects.all().filter(is_available=True)
    context = {
        'products':products,
    }
    return render(request, 'shop/index.html', context)

def store(request, category_slug = None):
    # return HttpResponse("Hello Magic")

    categories = None
    products = None

    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category = categories, is_available=True)
        product_count = products.count()
    else:
        products = Product.objects.all().filter(is_available=True)
        product_count = products.count()
    context = {
        'products':products,
        'product_count':product_count,
    }
    return render(request, 'shop/store.html', context)