# Generated by Django 3.2.5 on 2021-07-13 19:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('packages', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='package',
            name='stripe_price_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
