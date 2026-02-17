from django.db import models
from django.contrib.auth.models import User
from store.models import Product

# orders/models.py
class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders"
    )
    full_name = models.CharField(max_length=150, blank=True, default="Guest")
    email = models.EmailField(blank=True, default="guest@example.com")
    phone_number = models.CharField(max_length=20, blank=True, default="N/A")
    address = models.CharField(max_length=255, blank=True, default="N/A")
    city = models.CharField(max_length=100, blank=True, default="N/A")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    paid = models.BooleanField(default=False)
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return f"Order #{self.id} - {self.full_name}"

    @property
    def total_price(self):
        return sum(item.price * item.quantity for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField(default=1)

    def save(self, *args, **kwargs):
        if not self.price:
            self.price = self.product.price
        super().save(*args, **kwargs)

