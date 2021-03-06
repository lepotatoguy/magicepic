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
    path('dashboard/', views.dashboard, name='dashboard'),
    path('forgotPassword/', views.forgotPassword, name='forgotPassword'),
    path('resetPassword/', views.resetPassword, name='resetPassword'),
    path('logout/', views.logout, name='logout'),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
    path('resetpassword_validate/<uidb64>/<token>', views.resetpassword_validate, name='resetpassword_validate'),
    path('store/search/', views.search, name='search'),
    path('add_cart/<int:product_id>', views.add_cart, name='add_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('remove_cart/<int:product_id>/<int:cart_item_id>', views.remove_cart, name='remove_cart'),
    path('remove_cart_item/<int:product_id>/<int:cart_item_id>', views.remove_cart_item, name='remove_cart_item'),
    path('store/category/<slug:category_slug>', views.store, name='products_by_category'),
    path('store/category/<slug:category_slug>/<slug:product_slug>', views.product_detail, name='product_detail'),
    path('place_order/', views.place_order, name='place_order'),
    path('payments/', views.payments, name='payments'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)