from django.db import models
from django.conf import settings
from packages.models import Package

import uuid

# Create your models here.

class Order(models.Model):
    order_id = models.IntegerField(null=False, blank=False, unique=True, editable=False)
    buyer_name = models.CharField(max_length=50, blank=False, null=False)
    buyer_email = models.EmailField(max_length=155, blank=False, null=False)
    date = models.DateTimeField(auto_now_add=True)
    order_total = order_total = models.DecimalField(max_digits=10, decimal_places=2, null=False, default=0)

    def _create_order_number(self):
        """Generate randomised order number using UUID"""
        return uuid.uuid4().hex.upper()

    def save(self, *args, **kwargs):
        """Set order ID if not already set"""

        if not self.order_id:
            self.order_id = self._create_order_number()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_number


class OrderItem(models.Model):
    order = models.ForeignKey(Order, null=False, blank=False, on_delete=models.CASCADE, related_name='order_item')
    package = models.ForeignKey(Package, null=False, blank=False, on_delete=models.CASCADE, related_name='order_package')
    quantity = models.IntegerField(null=False, blank=False, default=0)
    item_total = models.DecimalField(max_digits=6, decimal_places=2, null=False, blank=False, editable=False)

    def save(self):

        self.item_total = self.package.price * self.quantity
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f'Package: {self.package.name}, Order: {self.order.order_id}'