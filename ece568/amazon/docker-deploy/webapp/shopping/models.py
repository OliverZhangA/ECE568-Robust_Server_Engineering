from itertools import product
from tkinter import CASCADE
from apt import Cache
from django.db import models

# Create your models here.

from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now

#catalog for different kinds of products
class catalog(models.Model):
    cate_name = models.CharField(max_length=100, null=False, blank=False)
    def __str__(self):
        return str(self.cate_name)

#initialize a series of warehouses
class warehouse(models.Model):
    #need to get warehouse id??
    pos_x = models.IntegerField(default=0)
    pos_y = models.IntegerField(default=0)

    def __str__(self):
        return "(" + str(self.x) + ", " + str(self.y) + ")"

class product(models.Model):
    product_name = models.CharField(max_length=100, null=False, blank=False)
    product_amt = models.IntegerField(default=0)
    product_price = models.FloatField(default=0)
    product_catalog = models.ForeignKey(catalog, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return str(self.product_name)

class order(models.Model):
    #owner
    owner = models.ForeignKey(User, on_delete=CASCADE, blank=False, null=False)
    #order_time
    order_time = models.DateTimeField(default=now)
    #product
    product = models.ForeignKey(product)
    product_amt = models.IntegerField(default=1)
    #package status??
    package_info = models.ForeignKey(package_info, blank=False, null=False)

    def __str__(self):
        return "order time:" + str(self.order_time) + ", product:" + str(product) + "*" + str(self.product_amt) + "in package:" + str(package_info)

class package_info(models.Model):
    owner = models.ForeignKey(User, on_delete=CASCADE, blank=False, null=False)
    from_wh = models.ForeignKey(warehouse, on_delete=models.SET_NULL)
    dest_x = models.IntegerField(blank=False, null=False)
    dest_y = models.IntegerField(blank=False, null=False)
    package_job_time = models.DateTimeField(default=now)
    status = models.CharField(blank=False, null=False)
    ups_account = models.CharField(max_length=100, blank=True, null=True)
    def __str__(self):
        return "<" + str(self.warehouse) + ", " + self.status + ">"

    def show_order(self):
        order_detail="order has been placed with following items:\n"
        for order in self.orders.all():
            order_detail+="+ %s*%s\n" % (str(order.product), str(order.product_amt))
        return order_detail

    
