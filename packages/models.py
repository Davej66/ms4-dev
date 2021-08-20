from django.db import models

# Create your models here.


class Package(models.Model):
    tier = models.IntegerField(default=1, null=False, blank=False)
    stripe_price_id = models.CharField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    event_limit = models.IntegerField(default=1, null=False, blank=False)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return self.name