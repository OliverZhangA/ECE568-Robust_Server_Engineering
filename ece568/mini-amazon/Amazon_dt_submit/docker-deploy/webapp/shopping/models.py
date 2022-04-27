from itertools import product
from tkinter import CASCADE
from django.db import models

# Create your models here.

from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now

#catalog for different kinds of products
class catalog(models.Model):
    cate_name = models.CharField(max_length=100, null=False, blank=False)
    catalog_img = models.CharField(max_length=100, default="/static/imgs/cart.jpeg")
    def __str__(self):
        return str(self.cate_name)

#initialize a series of warehouses
class warehouse(models.Model):
    #need to get warehouse id??
    pos_x = models.IntegerField(default=0)
    pos_y = models.IntegerField(default=0)

    def __str__(self):
        return "(" + str(self.pos_x) + ", " + str(self.pos_y) + ")"

class commodity(models.Model):
    commodity_name = models.CharField(max_length=100, null=False, blank=False)
    commodity_amt = models.IntegerField(default=0)
    commodity_price = models.FloatField(default=0)
    commodity_catalog = models.ForeignKey(catalog, on_delete=models.SET_NULL, null=True)
    commodity_desc = models.CharField(max_length=200, blank=True, default="")
    commodity_img = models.CharField(max_length=100, default="/static/imgs/cart.jpeg")
    seller_email = models.CharField(max_length=100, blank=True, default="1148201178@qq.com")
    seller = models.CharField(max_length=100, null=True, blank=True, default="BBBuy")
    def __str__(self):
        return str(self.commodity_name)

class package_info(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=False)
    from_wh = models.ForeignKey(warehouse, on_delete=models.SET_NULL, null=True)
    dest_x = models.IntegerField(default=0, blank=False, null=False)
    dest_y = models.IntegerField(default=0, blank=False, null=False)
    package_job_time = models.DateTimeField(default=now)
    status = models.CharField(default = "",max_length=10, blank=False, null=False)
    ups_account = models.CharField(max_length=100, blank=True, null=True)
    estimate_arrtime = models.DateTimeField(default=now)
    is_gift = models.BooleanField(blank=False, null=False, default=False)
    blessing = models.CharField(max_length=300, blank=True, null=True)
    def __str__(self):
        return "<" + str(self.from_wh) + ", " + self.status + ">"
    def info(self):
        order_detail="Your order has been placed with following items:\n"
        order_detail+="------------------\n"
        for order in self.order_set.all():
            order_detail+="+++ %s*%s\n" % (str(order.commodity), str(order.commodity_amt))
        order_detail+="\n------------------\n"
        return order_detail

class order(models.Model):
    #owner
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=False)
    #order_time
    order_time = models.DateTimeField(default=now)
    #commodity
    commodity = models.ForeignKey(commodity, on_delete=models.CASCADE, null=True)
    commodity_amt = models.IntegerField(default=1)
    #package status??
    package_info = models.ForeignKey(package_info, on_delete=models.CASCADE, blank=False, null=True)
    def __str__(self):
        return "order time:" + str(self.order_time) + ", commodity:" + str(commodity) + "*" + str(self.commodity_amt) + "in package:" + str(package_info)



    
