from django.urls import path
from . import views

app_name = 'products'
urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('brand/<slug:brand_slug>/', views.product_list_by_brand, name='product_list_by_brand'),
    path('<slug:category_slug>/', views.product_list, name='product_list_by_category'),
    path('product/<int:id>/<slug:slug>/', views.product_detail, name='product_detail'),
    path('ajax/search/', views.ajax_search, name='ajax_search'),
]