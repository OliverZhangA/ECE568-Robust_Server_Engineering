# Generated by Django 4.0.1 on 2022-04-22 14:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopping', '0008_package_info_estimate_arrtime'),
    ]

    operations = [
        migrations.AlterField(
            model_name='package_info',
            name='status',
            field=models.CharField(default='', max_length=10),
        ),
    ]