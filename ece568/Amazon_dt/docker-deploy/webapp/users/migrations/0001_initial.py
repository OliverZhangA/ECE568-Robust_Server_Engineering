# Generated by Django 4.0.1 on 2022-04-18 00:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DriverProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, null=True)),
                ('ID_num', models.CharField(max_length=20, null=True)),
                ('DOB', models.DateTimeField(default=django.utils.timezone.now)),
                ('image', models.ImageField(default='default.gif', upload_to='profile_pics')),
                ('vehicle_type', models.CharField(choices=[('Sedan', 'Sedan'), ('Coupe', 'Gold'), ('SUV', 'SUV'), ('Minivan', 'Minivan')], max_length=50)),
                ('vehicle_capacity', models.IntegerField(default=0)),
                ('plate_num', models.CharField(max_length=7)),
                ('license_num', models.CharField(max_length=12)),
                ('special_info', models.TextField(blank=b'I01\n', max_length=200)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='driverprofile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]