# Generated by Django 3.2.6 on 2021-08-17 11:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0005_alter_event_registrants'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='timezone',
            field=models.CharField(default='GMT', max_length=3),
        ),
    ]