from django.contrib import admin
from .models import catalog, commodity, order, package_info, warehouse
# Register your models here.
admin.site.register(catalog)
admin.site.register(commodity)
admin.site.register(order)
admin.site.register(package_info)
admin.site.register(warehouse)