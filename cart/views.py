from django.shortcuts import render, get_object_or_404, redirect
from products.models import Product
from .models import Cart, CartItem
from django.views.decorators.http import require_POST
from django.http import JsonResponse
import json


def get_user_cart(request, user=None):

    cart = None

    if user and user.is_authenticated:
        cart = Cart.objects.filter(user=user, is_active=True).first()

        cart_id = request.session.get('cart_id')
        if cart_id:
            try:
                session_cart = Cart.objects.get(id=cart_id, user__isnull=True)
                if cart:
                    for item in session_cart.items.all():
                        existing_item = cart.items.filter(product=item.product).first()
                        if existing_item:
                            existing_item.quantity += item.quantity
                            existing_item.save()
                        else:
                            item.cart = cart
                            item.save()
                    session_cart.delete()
                else:
                    session_cart.user = user
                    session_cart.save()
                    cart = session_cart
                del request.session['cart_id']
            except Cart.DoesNotExist:
                pass

    if not cart:
        cart_id = request.session.get('cart_id')
        if cart_id:
            try:
                cart = Cart.objects.get(id=cart_id, user__isnull=not (user and user.is_authenticated))
            except Cart.DoesNotExist:
                cart = None

        if not cart:
            cart = Cart.objects.create(user=user if user and user.is_authenticated else None)
            if not (user and user.is_authenticated):
                request.session['cart_id'] = cart.id

    return cart


@require_POST
def cart_add(request, product_id):
    cart = get_user_cart(request, request.user if request.user.is_authenticated else None)

    product = get_object_or_404(Product, id=product_id)

    try:
        data = json.loads(request.body)
        quantity = int(data.get('quantity', 1))
        quantity = max(1, quantity)
    except (ValueError, json.JSONDecodeError):
        quantity = 1

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': quantity}
    )

    if not created:
        cart_item.quantity += quantity
        cart_item.save()

    return JsonResponse({
        "success": True,
        "message": f'Added {quantity} x {product.name} to cart',
        "cart_total": cart.get_total_quantity(),
        "item_count": cart.items.count()
    })

def cart_detail(request):
    cart = None
    shipping_cost = 0
    total_cart = 0

    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user, is_active=True)
        except Cart.DoesNotExist:
            pass
    else:
        cart_id = request.session.get('cart_id')
        if cart_id:
            try:
                cart = Cart.objects.get(id=cart_id, user__isnull=True)
            except Cart.DoesNotExist:
                pass

    if cart and not cart.items.exists():
        cart = None

    if cart:
        shipping_cost = cart.get_shipping_cost()
        total_cart = cart.get_total_price() + shipping_cost

    return render(request, 'cart/detail.html', {
        'cart': cart,
        'shipping_cost': shipping_cost,
        'total_cart': total_cart
    })


def cart_remove(request, product_id):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user, is_active=True).first()
    else:
        cart_id = request.session.get('cart_id')
        cart = Cart.objects.filter(id=cart_id).first() if cart_id else None

    if not cart:
        return redirect('cart:cart_detail')

    try:
        item = CartItem.objects.get(id=product_id, cart=cart)
        item.delete()
    except CartItem.DoesNotExist:
        pass

    return redirect('cart:cart_detail')


def cart_clear(request):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user, is_active=True).first()
    else:
        cart_id = request.session.get('cart_id')
        cart = Cart.objects.filter(id=cart_id).first() if cart_id else None

    if cart:
        cart.items.all().delete()

    return redirect('cart:cart_detail')

