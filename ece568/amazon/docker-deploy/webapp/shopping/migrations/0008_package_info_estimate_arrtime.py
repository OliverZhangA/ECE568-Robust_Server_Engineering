# Generated by Django 4.0.1 on 2022-04-22 00:45

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('shopping', '0007_catalog_catalog_img_alter_commodity_commodity_img'),
    ]

    operations = [
        migrations.AddField(
            model_name='package_info',
            name='estimate_arrtime',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
