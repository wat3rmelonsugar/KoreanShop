from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from .models import Order


@shared_task
def send_order_confirmation(order_id, user_email=None):
    order = Order.objects.get(id=order_id)
    subject = f'Заказ №{order.id} подтверждён'
    message = render_to_string('orders/order_email.html', {'order': order})

    recipient_email = user_email if user_email else order.email

    send_mail(
        subject,
        message,
        'yab18@tpu.ru',
        [recipient_email],
        fail_silently=False,
        html_message=message
    )