# Generated by Django 4.0.1 on 2022-01-26 17:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rides', '0003_alter_orderinfo_dest_addr_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='rideowner',
            old_name='ride_order',
            new_name='orderinfo',
        ),
    ]