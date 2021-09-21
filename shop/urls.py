from magicepic_website.settings import MEDIA_ROOT
from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.index, name='index'),
    path('store/', views.store, name='store'),
    path('store/<slug:category_slug>', views.store, name='products_by_category'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)