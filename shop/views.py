from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404, redirect, render
from shop.forms import RegistrationForm
from shop.models import *
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q #works as OR Operator
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from .forms import *
from datetime import datetime
import requests

#Email Verification

from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail, BadHeaderError, EmailMultiAlternatives



# Create your views here.
from django.http import HttpResponse
from decouple import config

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
    current_user = request.user
    product = Product.objects.get(id=product_id) #getting the product
    if current_user.is_authenticated:    #if the user is  authenticated
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

        is_cart_item_exists = CartItem.objects.filter(product=product, user=current_user).exists()
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product, user=current_user)
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
                user=current_user,
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
                user=current_user,
            )
            if(len(product_variation)>0):
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.quantity += 1 
            cart_item.save()
        return redirect('cart')
    #if the user is not authenticated
    else:    
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
    
    product = get_object_or_404(Product, id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product, user = request.user, id=cart_item_id)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request)) #getting the cart using the cart_id present in the session
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
    
    product = get_object_or_404(Product, id=product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(product=product, user = request.user, id=cart_item_id)
    else: 
        cart = Cart.objects.get(cart_id=_cart_id(request)) #getting the cart using the cart_id present in the session
        cart_item = CartItem.objects.get(product=product, cart = cart, id=cart_item_id)
    cart_item.delete()
    return redirect('cart')

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
            to_mail =  email
            subject = "Please activate your account - MagicEpic"
            subject, from_email, to = f'{subject}', 'joyanta.csebracu@gmail.com', f'{to_mail}' # 'no_reply@magicepic-bd.com', 
            cc_email = ['a.t.m.masum.billah@g.bracu.ac.bd']
            text_content = ''
            html_content = render_to_string('shop/accounts/account_verification_email.html', {
                 'user': user,
                 'domain': current_site,
                 'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                 'token': default_token_generator.make_token(user),
             })

            try:
                msg = EmailMultiAlternatives(subject, text_content, from_email, [to]
                # ,cc=cc_email
                )
                msg.attach_alternative(html_content, "text/html")
                # msg.attach_file(location/to/path)
                msg.send()
                print("True")
                success = True
            except:
                print('mail does not send to -', to_mail)
            print(to_mail)
            return redirect('/login/?command=verification&email='+to_mail)    
    else:
        form = RegistrationForm()
    context = {
        'form': form,
    }
    return render(request, 'shop/accounts/register.html', context)

def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulations! Your account is successfully activated!')
        return redirect('login')
    else:
        messages.error(request, 'Invalid activation link')
        return redirect('register')


def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email,password=password)

        if user is not None:
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)

                    #Getting the product variation by cart id
                    product_variation = []
                    for item in cart_item:
                        variation = item.variations.all()
                        product_variation.append(list(variation))

                    #Get the cart items from the user to access his product variations
                    cart_item = CartItem.objects.filter(user=user)
                    #existing_vatiations coming from db
                    #current variations product_variation
                    #item_id coming from db
                    existing_variation_list = []
                    id = []
                    for item in cart_item:
                        existing_variation = item.variations.all()
                        existing_variation_list.append(list(existing_variation))
                        id.append(item.id)

                    #looking into product variation and existing variation list to get the common
                    for pr in product_variation:
                        if pr in existing_variation_list:
                            index = existing_variation_list.index(pr)
                            item_id = id[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity += 1
                            item.user = user
                            item.save()
                        else:
                            cart_item = CartItem.objects.filter(cart=cart)
                            for item in cart_item:
                                item.user = user
                                item.save()
                    
            except:
                pass
            auth.login(request, user)
            messages.success(request, "You are now logged in.")
            # url = request.META.get('HTTP_REFERER')
            url = request.META.get("HTTP_REFERER", "")
            print('url -> ', url)
            try:
                query = requests.utils.urlparse(url).query
                print('query ->', query)
                params = dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    nextPage = params['next']
                    return redirect(nextPage)
            except:
                return redirect('dashboard')
        else:
            messages.error(request, "Invalid login credentials.")
            return redirect('login')
    return render(request, 'shop/accounts/login.html')

@login_required(login_url = "login")
def logout(request):
    auth.logout(request)
    messages.success(request, "You are now logged out.")
    return redirect('login')

@login_required(login_url = "login")
def dashboard(request):
    return render(request,'shop/accounts/dashboard.html')

def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)
        # Reset Password
            current_site = get_current_site(request)
            to_mail =  email
            subject = "Reset Your Password - MagicEpic"
            subject, from_email, to = f'{subject}', 'joyanta.csebracu@gmail.com', f'{to_mail}' # 'no_reply@magicepic-bd.com',
            cc_email = ['a.t.m.masum.billah@g.bracu.ac.bd']
            text_content = ''
            html_content = render_to_string('shop/accounts/reset_password_email.html', {
                 'user': user,
                 'domain': current_site,
                 'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                 'token': default_token_generator.make_token(user),
             })

            try:
                msg = EmailMultiAlternatives(subject, text_content, from_email, [to]
                # ,cc=cc_email
                )
                msg.attach_alternative(html_content, "text/html")
                # msg.attach_file(location/to/path)
                msg.send()
                print("True")
                success = True
                messages.success(request, 'Password Reset Email has been sent to your email address. If not found, please check it in Spam/Others/All Mail Folder(s).')
                return redirect('login')
            except:
                print('mail does not send to -', to_mail)    
        
        else:
            messages.error(request, 'Account does not exist.')
            return redirect('forgotPassword')
    return render(request,'shop/accounts/forgotPassword.html')

def resetpassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Please reset your password')
        return redirect('resetPassword')
    else:
        messages.error(request, 'Link Expired/ Invalid Link')
        return redirect('login')

def resetPassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            messages.success(request, 'Password reset successful!')
            return redirect('login')
        else:
            messages.error(request, 'Password do not match!')
            return redirect('resetPassword')
    else:
        return render(request, 'shop/accounts/resetPassword.html')


#the final cart function

def cart(request, total=0, quantity=0, cart_items=None):
    discount_code = ""
    discount_amount = 0
    discount = 0
    discount_amount_percent = 0
    location = ""
    if 'location' in request.POST:
        location = request.POST['location']
        location = int(location)
    if 'discount' in request.POST:
        #Firstly listing all the promos available in discount list
        discount_promo_list = []
        discount_promos = Discount.objects.filter(is_active=True)
        for promo in discount_promos:
            discount_promo_list.append(promo.promo_code)
        discount = request.POST['discount']
        discount_code = request.POST['discount']
        # print("Discount Code inserted:", discount)
        # print(discount_promo_list)
        if discount in discount_promo_list:
            discount_amount_percent = Discount.objects.get(promo_code=discount).percent
            discount_amount = Discount.objects.get(promo_code=discount).amount
        else:
            discount_amount = -1 #Represents discount being not active
            discount_amount_percent = -1
    try:
        delivery_cost = 0 
        grand_total = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        if location == 0: #Outside Dhaka
            delivery_cost = 120 
        elif location == 1:
            delivery_cost = 60
        else:
            delivery_cost = 120 #by default 120 Taka. 
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
    dd = Cart_Discount_Delivery(user=request.user,delivery_cost=delivery_cost, discount = discount)
    dd.save()
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


@login_required(login_url = "login")
def checkout(request, total=0, quantity=0, cart_items=None, location= 0):
    discount_code = ""
    discount_amount = 0
    discount = 0
    discount_amount_percent = 0
    location = ""
    if 'location' in request.POST:
        location = request.POST['location']
        location = int(location)
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
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        obj = Cart_Discount_Delivery.objects.filter(user=request.user).last()
        discount = obj.discount
        delivery_cost = obj.delivery_cost
        # discount = Cart_Discount_Delivery.objects.get(user=request.user).discount.last()
        # delivery_cost = Cart_Discount_Delivery.objects.get(user=request.user).delivery_cost.last()
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
    

    return render(request, 'shop/checkout.html', context)

# Order

def place_order(request,total=0, quantity=0):

    current_user = request.user

    #If cart item is less or equal to 0, redirect to shop
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')
    
    total = 0
    obj = Cart_Discount_Delivery.objects.filter(user=request.user).last()
    discount = obj.discount
    delivery_cost = obj.delivery_cost
    quantity = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    total = total + delivery_cost - discount

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            #Store all the billing info inside order table
            dd = Cart_Discount_Delivery()
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.district = form.cleaned_data['district']
            data.city = form.cleaned_data['city']
            data.delivery_cost = delivery_cost
            data.discount = discount
            # print(dd.delivery_cost)
            # data.delivery_cost = dd.delivery_cost
            # data.discount = dd.discount
            # if data.city.lower() == "dhaka":
            #     delivery_cost = 60
            # else:
            #     delivery_cost = 120
            data.order_note = form.cleaned_data['order_note']
            data.total = total
            data.delivery_cost = delivery_cost #not sure how the delivery cost will work
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()
            #generate order id
            now = datetime.now()
            year = now.strftime('%Y')
            date = now.strftime('%d')
            month = now.strftime('%m')
            current_date = year+month+date #20211230
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()
            instance = Cart_Discount_Delivery.objects.filter(user=request.user)
            instance.delete()
            return HttpResponse("order successful")
        else:
            return HttpResponse("something went wrong")
        
    else:
        return HttpResponse("order failed")

def payments():
    return HttpResponse("payment")