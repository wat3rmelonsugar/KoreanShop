from django.shortcuts import render, redirect, get_object_or_404
from cart.models import Cart
from .forms import OrderCreateForm
from .models import OrderItem, Order
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import  Order, OrderItem
from cart.views import get_user_cart
from .tasks import send_order_confirmation

from .tasks import send_order_confirmation  # Импортируем задачу Celery


def order_create(request):
    cart = get_user_cart(request, request.user if request.user.is_authenticated else None)

    if not cart or not cart.items.exists():
        messages.error(request, "Your cart is empty!")
        return redirect('cart:cart_detail')

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)

            if request.user.is_authenticated:
                order.user = request.user
                if not order.email and request.user.email:
                    order.email = request.user.email

            order.save()

            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price
                )

            cart.is_active = False
            cart.save()

            if not request.user.is_authenticated and 'cart_id' in request.session:
                del request.session['cart_id']

            recipient_email = None
            if request.user.is_authenticated and request.user.email:
                recipient_email = request.user.email

            #send_order_confirmation.delay(order.id, user_email=recipient_email)

            return redirect('orders:order_confirmation', order_id=order.id)

    else:
        initial = {}
        if request.user.is_authenticated:
            initial.update({
                'full_name': request.user.get_full_name(),
                'email': request.user.email,
            })
        form = OrderCreateForm(initial=initial)

    context = {
        'form': form,
        'cart': cart,
        'total': cart.get_total_price(),
        'shipping_cost': cart.get_shipping_cost(),
        'grand_total': cart.get_total_price() + cart.get_shipping_cost(),
    }

    return render(request, 'orders/order_create.html', context)


def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'orders/order_confirmation.html', {'order':order})