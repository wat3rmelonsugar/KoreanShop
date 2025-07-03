from django.urls import path
from .views import cart_add, cart_detail, cart_remove, cart_clear, update_cart

app_name = 'cart'
urlpatterns = [
    path('add/<int:product_id>', cart_add, name='cart_add'),
    path('', cart_detail, name='cart_detail'),
    path('remove/<int:product_id>/', cart_remove, name='remove_item'),
    path('clear/', cart_clear, name='cart_clear'),
    path('update/', update_cart, name='update_cart'),
]