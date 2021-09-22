from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404, redirect, render
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

def product_detail(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug = product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id = _cart_id(request), product=single_product).exists()
        
    except Exception as e:
        raise e
    
    context = {
        'single_product':single_product,
        'in_cart':in_cart,
    }
    return render(request, 'shop/product_detail.html', context)


def cart(request):
    return render(request, 'shop/cart.html')

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def add_cart(request, product_id):
    product = Product.objects.get(id=product_id) #getting the product
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request)) #getting the cart using the cart_id present in the session
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cart_id = _cart_id(request)
        )
    cart.save()

    try:
        cart_item = CartItem.objects.get(product=product, cart = cart)
        cart_item.quantity += 1 
        cart_item.save()
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(
            product = product,
            quantity = 1,
            cart = cart,
        )
        cart_item.save()
    return redirect('cart')

def remove_cart(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request)) #getting the cart using the cart_id present in the session
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart = cart)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart')

def remove_cart_item(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request)) #getting the cart using the cart_id present in the session
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart = cart)
    cart_item.delete()
    return redirect('cart')

def cart(request, total=0, quantity=0, cart_items=None):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        delivery_cost = 60 #for now inside dhaka.
        discount = 100 
        grand_total = total + delivery_cost - discount
    except ObjectDoesNotExist:
        pass
    
    context = {
        'total':total,
        'quantity':quantity,
        'cart_items':cart_items,
        'delivery_cost':delivery_cost,
        'grand_total':grand_total,
        'discount':discount,
    }
    

    return render(request, 'shop/cart.html', context)
