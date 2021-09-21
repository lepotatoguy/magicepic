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