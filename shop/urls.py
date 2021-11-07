from magicepic_website.settings import MEDIA_ROOT
from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.index, name='index'),
    path('store/', views.store, name='store'),
    path('cart/', views.cart, name='cart'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
    path('store/search/', views.search, name='search'),
    path('add_cart/<int:product_id>', views.add_cart, name='add_cart'),
    path('remove_cart/<int:product_id>/<int:cart_item_id>', views.remove_cart, name='remove_cart'),
    path('remove_cart_item/<int:product_id>/<int:cart_item_id>', views.remove_cart_item, name='remove_cart_item'),
    path('store/category/<slug:category_slug>', views.store, name='products_by_category'),
    path('store/category/<slug:category_slug>/<slug:product_slug>', views.product_detail, name='product_detail'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)