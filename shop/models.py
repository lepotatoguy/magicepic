from django.db import models
from django.db.models.aggregates import Variance
from django.urls import reverse
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# Create your models here.

class Category(models.Model):
    category_name = models.CharField(max_length=100, unique = True)
    slug = models.SlugField(max_length=1000, unique = True)
    description = models.TextField(max_length = 2000, blank=True)
    category_image = models.ImageField(upload_to='photos/categories/')

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def get_url(self):
        return reverse('products_by_category', args=[self.slug])

    def __str__(self):
        return self.category_name

class AccountManager(BaseUserManager):
    def create_user(self, first_name, last_name, username, email, password=None):
        if not email:
            raise ValueError("User must have an email address")

        if not username:
            raise ValueError("User must have an username")

        user = self.model(
            email = self.normalize_email(email),
            username = username,
            first_name = first_name,
            last_name = last_name,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, first_name, last_name, username, email, password):
        user = self.create_user(
            email = self.normalize_email(email),
            username = username,
            password= password,
            first_name = first_name,
            last_name = last_name,
        )

        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.is_superadmin = True
        user.save(using=self._db)
        return user
    


class Account(AbstractBaseUser):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50, unique = True)
    email = models.EmailField(max_length=50, unique = True)
    phone_number = models.CharField(max_length=11)
    
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default = False)
    is_staff = models.BooleanField(default = False)
    is_active = models.BooleanField(default = False)
    is_superadmin = models.BooleanField(default = False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name',]
    
    objects = AccountManager()
    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, add_label):
        return True

class Product(models.Model):
    product_name = models.CharField(max_length=200, unique = True)
    slug = models.SlugField(max_length=1000, unique = True)
    description = models.TextField(max_length = 2000, blank=True)
    price = models.IntegerField()
    image = models.ImageField(upload_to='photos/products/')
    stock = models.IntegerField() #stock
    is_available = models.BooleanField(default = False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def get_url(self):
        return reverse('product_detail', args=[self.category.slug, self.slug])

    def __str__(self):
        return self.product_name



class Discount(models.Model):
    promo_code = models.CharField(max_length=200, unique = True)
    date_end = models.DateTimeField()
    percent = models.IntegerField()
    amount = models.IntegerField()
    is_active = models.BooleanField(default = False)

    def __str__(self):
        return self.promo_code

class VariationManager(models.Manager):
    def varient(self): #If needed, more functions will be added. more function = more varient
        return super(VariationManager, self).filter(variation_category='varient', is_active=True)
variation_category_choice = (
    ('varient', 'varient'),
    # ('color', 'color'),
)
class Variation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation_category = models.CharField(max_length=200, choices=variation_category_choice)
    variation_value = models.CharField(max_length=200)
    # quantity = models.IntegerField()
    date_created = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default = True)

    def __str__(self):
        return self.variation_value


class Cart(models.Model):
    cart_id = models.CharField(max_length=200, blank = True)
    date_added = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return self.cart_id

class CartItem(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variations = models.ManyToManyField(Variation, blank=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, null=True)
    quantity = models.IntegerField()
    is_active = models.BooleanField(default = True)

    def sub_total(self):
        return self.product.price * self.quantity

    def __unicode__(self):
        return self.product


#order

class Payment(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE) 
    payment_id = models.CharField(max_length=200)
    payment_method = models.CharField(max_length=200)
    amount_paid = models.CharField(max_length=200)
    status = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.payment_id

class Cart_Discount_Delivery(models.Model): #for cart discounts and delivery cost
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    delivery_cost = models.IntegerField()
    discount = models.FloatField()


class Order(models.Model):
    STATUS = (
        ('New', 'New'),
        ('Accepted', 'Accepted'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True) 
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True) 
    order_number = models.CharField(max_length=200)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=200)
    email = models.EmailField(max_length=200)
    address_line_1 = models.CharField(max_length=200)
    address_line_2 = models.CharField(max_length=200)
    district = models.CharField(max_length=200)
    city = models.CharField(max_length=200)
    total = models.CharField(max_length=200)
    delivery_cost = models.IntegerField(default=120)
    discount = models.FloatField(default=0)
    status = models.CharField(max_length=200, choices=STATUS, default='New')
    ip = models.CharField(max_length=200)
    order_note = models.CharField(max_length=200)
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} {} {}'.format(self.order_number, self.first_name, self.last_name)

class OrderProduct(models.Model):

    order = models.ForeignKey(Order, on_delete=models.CASCADE) 
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE) 
    variation = models.ForeignKey(Variation, on_delete=models.CASCADE)   
    order_number = models.CharField(max_length=200)
    color = models.CharField(max_length=200)
    size = models.CharField(max_length=200)
    quantity = models.IntegerField()
    product_price = models.FloatField()
    ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product.product_name

