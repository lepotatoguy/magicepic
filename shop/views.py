from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404, redirect, render
from shop.forms import RegistrationForm
from shop.models import *
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q #works as OR Operator
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required

#Email Verification

from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

# Create your views here.
from django.http import HttpResponse

#returns home page
def index(request):
    # return HttpResponse("Hello Magic")
    products = Product.objects.all().filter(is_available=True)
    context = {
        'products':products,
    }
    return render(request, 'shop/index.html', context)

#returns the whole store with all products
def store(request, category_slug = None):
    # return HttpResponse("Hello Magic")

    categories = None
    products = None

    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category = categories, is_available=True)
        paginator = Paginator(products, 3)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()
    else:
        products = Product.objects.all().filter(is_available=True).order_by('id')
        paginator = Paginator(products, 6)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()
    context = {
        'products':paged_products,
        'product_count':product_count,
    }
    return render(request, 'shop/store.html', context)

# product detail from store

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


#cart part

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def add_cart(request, product_id):
    product = Product.objects.get(id=product_id) #getting the product
    product_variation = []
    if request.method == "POST":
        for item in request.POST:
            key = item
            value = request.POST[key]
        # varient = request.POST['varient']
        try:
            variation = Variation.objects.get(product = product, variation_category__iexact = key, variation_value__iexact = value)
            product_variation.append(variation)
        except:
            pass
    
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request)) #getting the cart using the cart_id present in the session
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cart_id = _cart_id(request)
        )
    cart.save()

    is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()
    if is_cart_item_exists:
        cart_item = CartItem.objects.filter(product=product, cart = cart)
        #existing_vatiations coming from db
        #current variations product_variation
        #item_id coming from db
        existing_variation_list = []
        id = []
        for item in cart_item:
            existing_variation = item.variations.all()
            existing_variation_list.append(list(existing_variation))
            id.append(item.id)

        if product_variation in existing_variation_list:
            #increase cart item quant
            index = existing_variation_list.index(product_variation)
            item_id = id[index]
            Item = CartItem.objects.get(product=product, id=item_id)
            Item.quantity += 1 
            Item.save()

        else:
            #create new cart item
            Item = CartItem.objects.create(
            product = product,
            quantity = 1,
            cart = cart,
        )
            if(len(product_variation)>0):
                Item.variations.clear()
                Item.variations.add(*product_variation) #* will make sure to add all the product variation
            # cart_item.quantity += 1 
            Item.save()
    else:
        cart_item = CartItem.objects.create(
            product = product,
            quantity = 1,
            cart = cart,
        )
        if(len(product_variation)>0):
            cart_item.variations.clear()
            cart_item.variations.add(*product_variation)
        cart_item.quantity += 1 
        cart_item.save()
    return redirect('cart')

def remove_cart(request, product_id, cart_item_id):
    cart = Cart.objects.get(cart_id=_cart_id(request)) #getting the cart using the cart_id present in the session
    product = get_object_or_404(Product, id=product_id)
    try:
        cart_item = CartItem.objects.get(product=product, cart = cart, id=cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect('cart')

def remove_cart_item(request, product_id, cart_item_id):
    cart = Cart.objects.get(cart_id=_cart_id(request)) #getting the cart using the cart_id present in the session
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart = cart, id=cart_item_id)
    cart_item.delete()
    return redirect('cart')

#the final cart function

def cart(request, total=0, quantity=0, cart_items=None):
    discount_code = ""
    discount_amount = 0
    discount = 0
    discount_amount_percent = 0
    if 'discount' in request.POST:
        #Firstly listing all the promos available in discount list
        discount_promo_list = []
        discount_promos = Discount.objects.filter(is_active=True)
        for promo in discount_promos:
            discount_promo_list.append(promo.promo_code)
        discount = request.POST['discount']
        discount_code = request.POST['discount']
        print("Discount Code inserted:", discount)
        print(discount_promo_list)
        if discount in discount_promo_list:
            discount_amount_percent = Discount.objects.get(promo_code=discount).percent
            discount_amount = Discount.objects.get(promo_code=discount).amount
        else:
            discount_amount = -1 #Represents discount being not active
            discount_amount_percent = -1
    try:
        delivery_cost = 0 
        grand_total = 0
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        delivery_cost = 60 #for now inside dhaka.
        # discount_amount = 100 
        if discount_amount_percent < 0 or discount_amount < 0: #Inactive/Not available discount added
            discount = -1
            grand_total = total + delivery_cost
        elif discount_amount_percent > 0 and discount_amount > 0: #Only Percentage wll be taken
            discount = (total*discount_amount_percent)/100
            grand_total = total - discount + delivery_cost
            print("Only Percentage taken but both were there")
        elif discount_amount_percent > 0: #Only percentage is given
            discount = (total*discount_amount_percent)/100
            grand_total = total - discount + delivery_cost
            print("Only Percentage taken")
        else: #Only amount is given
            discount = discount_amount
            grand_total = total - discount + delivery_cost
    except ObjectDoesNotExist:
        pass
    
    context = {
        'total':total,
        'quantity':quantity,
        'cart_items':cart_items,
        'delivery_cost':delivery_cost,
        'grand_total':grand_total,
        'discount_amount':discount_amount,
        'discount':discount,
        'discount_code':discount_code,
    }
    

    return render(request, 'shop/cart.html', context)

#search bar

def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            #works as OR Operator
            products = Product.objects.order_by('-date_created').filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword) )
            product_count = products.count()
    context = {
        'products':products,
        'product_count':product_count,

    }
    return render(request, 'shop/store.html', context)
    

#account registration and others

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username= email.split("@")[0]

            user = Account.objects.create_user(first_name=first_name, 
            last_name=last_name, email=email, password=password, username=username)
            user.phone_number = phone_number
            user.save()

            # User Activation
            current_site = get_current_site(request)
            mail_subject = "Please activate your account."
            message = render.to_string('accounts/account_verification_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user)
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            messages.success(request, "Registration Successful.")
            return redirect('register')
    else:
        form = RegistrationForm()
    context = {
        'form': form,
    }
    return render(request, 'shop/accounts/register.html', context)

def activate(request):
    return


def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email,password=password)

        if user is not None:
            auth.login(request, user)
            messages.success(request, "You are now logged in.")
            return redirect('index')
        else:
            messages.error(request, "Invalid login credentials.")
            return redirect('login')
    return render(request, 'shop/accounts/login.html')

@login_required(login_url = "login")
def logout(request):
    auth.logout(request)
    messages.success(request, "You are now logged out.")
    return redirect('login')