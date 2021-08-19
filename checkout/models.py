from django.db import models
from django.db.models import Sum
from django.conf import settings
from packages.models import Package
from users.models import MyAccount

import uuid


class Order(models.Model):
    order_id = models.CharField(max_length=50, blank=False, editable=False, unique=True)
    customer = models.ForeignKey(MyAccount, blank=False, null=True, on_delete=models.SET_NULL)
    buyer_name = models.CharField(max_length=50, blank=False, null=False)
    buyer_email = models.EmailField(max_length=155, blank=False, null=False)
    package_purchased = models.ForeignKey(Package, null=False, blank=False, default=1, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    order_total = models.DecimalField(max_digits=10, decimal_places=2, null=False, default=0)
    stripe_invoice_id = models.CharField(max_length=155, null=False, default='')

    def _create_order_number(self):
        """Generate randomised order number using UUID"""
        return str(uuid.uuid4().int)[:6]

    def save(self, *args, **kwargs):
        """Set order ID if not already set"""

        if not self.order_id:
            self.order_id = self._create_order_number()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_id