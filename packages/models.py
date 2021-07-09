from django.db import models

# Create your models here.


class Package(models.Model):
    tier = models.IntegerField(default=1, null=False, blank=False)
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return self.name