# Generated by Django 3.2.5 on 2021-08-07 17:59

from django.db import migrations, models
import users.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Roles',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role_name', models.CharField(default='', max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Skills',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('skill_name', models.CharField(default='', max_length=50)),
            ],
        ),
        migrations.RemoveField(
            model_name='myaccount',
            name='username',
        ),
        migrations.AddField(
            model_name='myaccount',
            name='package_name',
            field=models.CharField(default='Free Account', max_length=50),
        ),
        migrations.AddField(
            model_name='myaccount',
            name='package_tier',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='myaccount',
            name='profile_image',
            field=models.ImageField(blank=True, default=users.models.get_default_profile_image, null=True, upload_to=users.models.get_profile_image_filepath),
        ),
        migrations.AddField(
            model_name='myaccount',
            name='stripe_customer_id',
            field=models.CharField(blank=True, max_length=150, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='myaccount',
            name='stripe_subscription_id',
            field=models.CharField(blank=True, max_length=150, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='myaccount',
            name='first_name',
            field=models.CharField(default='', max_length=50),
        ),
        migrations.AlterField(
            model_name='myaccount',
            name='job_role',
            field=models.CharField(blank=True, default='', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='myaccount',
            name='last_name',
            field=models.CharField(default='', max_length=50),
        ),
        migrations.AlterField(
            model_name='myaccount',
            name='location',
            field=models.CharField(blank=True, default='', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='myaccount',
            name='skills',
            field=models.CharField(blank=True, default='', max_length=1000, null=True),
        ),
    ]