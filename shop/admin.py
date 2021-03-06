from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

# Register your models here.

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('category_name',)}
    list_display = ('category_name', 'slug')

admin.site.register(Category, CategoryAdmin)
class AccountAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'username', 'last_login', 'date_joined', 'is_active')
    list_display_links = ('email', 'first_name', 'last_name',)
    readonly_fields = ('last_login', 'date_joined')
    ordering = ('date_joined',)

    filter_horizontal=()
    list_filter = ()
    fieldsets = ()

admin.site.register(Account, AccountAdmin)

class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'price', 'image', 'stock', 'category', 'is_available', 'date_modified')
    prepopulated_fields = {'slug': ('product_name',)}


admin.site.register(Product, ProductAdmin)

class CartAdmin(admin.ModelAdmin):
    list_display = ('cart_id', 'date_added')

class CartItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'cart', 'quantity', 'is_active')


admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem, CartItemAdmin)
admin.site.register(Discount)


class VariationAdmin(admin.ModelAdmin):
    list_display = ('product', 'variation_value', 'is_active')
    list_editable = ('is_active',)
    list_filter = ('product', 'variation_value')
    # will add product variation here when more variation will be added 


admin.site.register(Variation, VariationAdmin)
admin.site.register(Order)
admin.site.register(Payment)
admin.site.register(OrderProduct)
admin.site.register(Cart_Discount_Delivery)