from django.contrib import admin
from .models import Order

# Register your models here.
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id','buyer_email', 'buyer_name', 'package_purchased', 'date')
    search_fields = ('order_id', 'buyer_email', 'package_purchased', 'date')
    readonly_fields = (
        'order_id',
        'buyer_email', 
        'buyer_name', 
        'package_purchased', 
        'date', 
        'stripe_invoice_id', 
        'order_total')
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

admin.site.register(Order, OrderAdmin)
