# Generated by Django 3.2.5 on 2021-07-17 21:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('checkout', '0006_remove_order_stripe_pid'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='stripe_invoice_id',
            field=models.CharField(default='', max_length=155),
        ),
    ]
