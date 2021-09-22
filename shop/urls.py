from magicepic_website.settings import MEDIA_ROOT
from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.index, name='index'),
    path('store/', views.store, name='store'),
    path('cart/', views.cart, name='cart'),
    path('store/<slug:category_slug>', views.store, name='products_by_category'),
    path('store/<slug:category_slug>/<slug:product_slug>', views.product_detail, name='product_detail'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)