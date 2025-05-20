from django.db import models
from products.models import Product
from django.contrib.auth import get_user_model

User = get_user_model()


class Cart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='carts'
    )
    is_active = models.BooleanField(default=True)  # Флаг активной корзины
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'is_active'],
                condition=models.Q(is_active=True),
                name='unique_active_cart'
            )
        ]

    def save(self, *args, **kwargs):
        # При создании новой активной корзины деактивируем старые
        if self.is_active and self.user:
            Cart.objects.filter(user=self.user, is_active=True).update(is_active=False)
        super().save(*args, **kwargs)

    def get_total_price(self):
        return sum(item.get_total_price() for item in self.items.all())

    def get_total_quantity(self):
        return sum(item.quantity for item in self.items.all())

    def get_shipping_cost(self):
        total = self.get_total_price()

        if total >= 2000:
            return 0
        elif total >= 1600:
            return 100
        elif total >= 1200:
            return 150
        elif total >= 800:
            return 200
        elif total >= 400:
            return 250
        else:
            return 300


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='cart_items', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def get_total_price(self):
        return self.product.price * self.quantity