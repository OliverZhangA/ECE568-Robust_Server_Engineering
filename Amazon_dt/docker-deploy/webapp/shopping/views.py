from functools import lru_cache
from itertools import product
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from users.models import DriverProfile
from .models import catalog, commodity, order, package_info, warehouse
from django.shortcuts import render, redirect
from django.urls import reverse
from .functions import buyandpack, match_warehouse
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.mail import send_mail
from email.mime.image import MIMEImage
from django.contrib.staticfiles.finders import find
from django.contrib.staticfiles import finders
from datetime import datetime, timedelta
import math
from django.db.models import Count
from django.contrib import messages
import time

# Create your views here.
class OrderList(ListView):
    model = order
    template_name = 'shopping/Orderlist.html'
    context_object_name = 'orders'
    ordering = ['commodity.commodity_name']
    def get_queryset(self):
        pk = self.kwargs['package_id']
        return order.objects.filter(package_info__id=pk)

class PackageList(ListView):
    model = package_info
    template_name = 'shopping/packagelist.html'
    context_object_name = 'packs'
    ordering = ['package_job_time']
    def post(self, request):
        context = {
            "packs": package_info.objects.filter(owner=self.request.user).order_by('-package_job_time')
        }
        if self.request.POST.get("action"):
            if self.request.POST["action"] == "arrived_orders":
                context["packs"]= package_info.objects.filter(owner=self.request.user).filter(status="delivered").order_by('-package_job_time')
            elif self.request.POST["action"] == "all_orders":
                context["packs"]= package_info.objects.filter(owner=self.request.user).order_by('-package_job_time')
            elif self.request.POST["action"] == "ongoing_orders":
                context["packs"]= package_info.objects.filter(owner=self.request.user).exclude(status="delivered").order_by('-package_job_time')
        return render(request, 'shopping/packagelist.html', context)
    def get_queryset(self):
        return package_info.objects.filter(owner=self.request.user).order_by('-package_job_time')

class CatelogList(ListView):
    model = catalog
    template_name = 'shopping/catalog.html'
    context_object_name = 'catas'
    ordering = ['cate_name']
    def get_queryset(self):
        #return OrderInfo.objects.filter(rideowner__user=self.request.user).exclude(status='complete').order_by('arrival_date')
        return catalog.objects.all
        #return OrderInfo.objects.filter(userid=self.request.user.id).exclude(status='complete').order_by('arrival_date')

class CataDetail(ListView):
    model = commodity
    template_name = 'shopping/commodity_list.html'
    context_object_name = 'commodities'
    ordering = ['commodity_name']
    def get_queryset(self):
        pk = self.kwargs['pk']
        return commodity.objects.filter(commodity_catalog__cate_name=pk)

class SearchResult(ListView):
    model = commodity
    template_name = 'shopping/commodity_list.html'
    context_object_name = 'commodities'
    ordering = ['commodity_name']
    def get_queryset(self):
        pk = self.kwargs['pk']
        queryset = commodity.objects.all()
        query_name = queryset.filter(commodity_name__icontains=pk)
        query_cata = queryset.filter(commodity_catalog__cate_name__icontains=pk)
        query_desc = queryset.filter(commodity_desc__icontains=pk)
        #return commodity.objects.filter(commodity_catalog__cate_name=pk)
        return query_name.union(query_cata).union(query_desc)

# class commodityDetail(DetailView):
#     model = commodity
#     template_name = 'shopping/commoditydetail.html'

def commodityDetail(request, pk1):
    commo = commodity.objects.get(pk=pk1)
    context = {
        'commodity' : 'commo'
    }
    if request.method == "POST":
        if request.POST.get("action"):
            if not request.user.is_authenticated:
                return redirect(reverse("login"))
            if request.POST["action"] == "buy":
                # create a new package
                amount = int(request.POST["count"])
                package = package_info()
                package.owner = request.user
                package.save()
                package.order_set.create(
                    owner=request.user,
                    commodity = commo,
                    commodity_amt = amount
                )
                # for order in package.order_set.all():
                #     order.save()
                print("--"+str(package.id)+"--")
                #buyandpack(package.id)
                #return HttpResponse("buy successful")
                return redirect(reverse("checkoutpage", kwargs={'package_id': package.id}))
            elif request.POST["action"] == "add":
                amount = int(request.POST["count"])
                try:
                    order_in_cart = order.objects.get(owner=request.user, commodity=commo, package_info__isnull=True)
                    order_in_cart.commodity_amt += amount
                    order_in_cart.save()
                except order.DoesNotExist:
                    neworder = order(owner=request.user, commodity=commo, commodity_amt=amount)
                    neworder.save()
                messages.success(request, "Adding to cart successfully!")
                # context = {
                #     "prompt" : "Adding to cart successfully"
                # }
                context['commo'] = commo
                return render(request, "shopping/commoditydetail.html", context)
        elif request.POST.get("sendemail"):
            #request.POST["sendemail"]
            subject = "Question from user: " + request.user.username
            message = "Product name: " + commo.commodity_name + "\nProduct recorded id: " + str(commo.id) + "\nMessage:\n------------------\n" + request.POST["content"] + "\n------------------\nand please reply to me at: \n" + request.POST["email"]
            email_from = settings.EMAIL_HOST_USER
            recipient_list1 = [request.user.email]
            send_mail(subject,message,email_from,recipient_list1)
            messages.success(request,"Your question has been sent to the seller, please wait for responses patiently, thanks for choosing us!")
            context['commo'] = commo
            print("sending email to" + commo.seller_email)
            return render(request, "shopping/commoditydetail.html", context)
        else:
            amount = int(request.POST["quantity"])
            package = package_info()
            package.owner = request.user
            package.is_gift = True
            if request.POST.get("blessing"):
                package.blessing = request.POST["blessing"]
            package.save()
            package.order_set.create(
                owner=request.user,
                commodity = commo,
                commodity_amt = amount
            )
            # for order in package.order_set.all():
            #     order.save()
            print("--"+str(package.id)+"--")
            #buyandpack(package.id)
            #return HttpResponse("buy successful")
            return redirect(reverse("checkoutpage", kwargs={'package_id': package.id}))

            
    else:
        context['commo'] = commo
        return render(request, "shopping/commoditydetail.html", context)

def shoppingCart(request):
    orders = order.objects.filter(owner=request.user).filter(package_info__isnull=True).order_by("order_time")
    if request.method == "POST":
        #operation = request.POST["operation"]
        if request.POST.get("delete"):
            orderid = request.POST["delete"]
            order.objects.get(pk=orderid).delete()
            return redirect(reverse("shoppingCart"))
        elif request.POST.get("checkout"):
            pck = package_info(owner=request.user)
            pck.save()
            for ord in orders:
                ord.package_info = pck
                ord.save()
            return redirect(reverse("checkoutpage", kwargs={'package_id': pck.id}))
        #print(request.POST["delete"])
        #operation = request.POST.get("operation")
        # if operation == "delete":
        #     print("&&&&&&&&&&going to delete&&&&&&&&&&&")
        #     orderid = request.POST["order_id"]
        #     order.objects.get(pk=orderid).delete()
        # #case that operation is checkout
        # elif operation == "checkout":
        #     pck = package_info(owner=request.user)
        #     for ord in orders:
        #         ord.package_info = pck
        #         ord.save()
        #     return redirect(reverse("checkout", kwargs={'package_id': pck.id}))
    context = {"orders": orders}
    return render(request, "shopping/shopping_cart.html", context)

def checkoutpage(request, package_id):
    pck = package_info.objects.get(id=package_id)
    if request.method == "POST":
        print("!!!!!!!!!!!!!!posting!!!!!!!!!!!!!!")
        #form = checkout_form(request.POST)
        if request.POST.get("cancel"):
            pck = package_info.objects.get(id=package_id)
            orders = order.objects.filter(owner=request.user).filter(package_info=pck).order_by("order_time")
            for ord in orders:
                ord.package_info = None
                ord.save()
            pck.delete()
            #to see if there are orders that can merge
            # order_in_cart = order.objects.get(owner=request.user, commodity=commo, package_info__isnull=True)
            # for ord in orders:
                
            #delete the package
            print("!!!!!!!!!!!!!!canceling!!!!!!!!!!!!!!")
            return redirect(reverse("shoppingCart"))
            #return HttpResponse("cancel checkout!!")
        elif request.POST.get("qcheckout"):
            print("!!!!!!!!!!!!!!checkingout!!!!!!!!!!!!!!")
            pck = package_info.objects.get(id=package_id)
            if pck.status != "":
                messages.warning(request, "You have already placed this order, do not repeat placing it!")
                return redirect(reverse("shopping-home"))
            curuserprofile = DriverProfile.objects.get(user=request.user.id)
            pck.dest_x = curuserprofile.dest_x
            pck.dest_y = curuserprofile.dest_y
            pck.ups_account = curuserprofile.UPS_account
            pck.status = "created"
            pck.save()
            print("8888888888888888"+str(type(pck.dest_x)))
            wh_id = match_warehouse(int(pck.dest_x), int(pck.dest_y))
            pck.from_wh = warehouse.objects.get(id=wh_id)
            #makeup offset from EST to EDT
            offset = timedelta(hours=1)
            pck.package_job_time = pck.package_job_time + offset
            #update the arrival time
            d = timedelta(hours=estimateArrtime(pck))
            pck.estimate_arrtime = pck.estimate_arrtime + offset + d
            pck.save()
            buyandpack(package_id)
            sendemail(pck)
            #turn to the checkout successful page!
            estarrtime = str(pck.estimate_arrtime)
            messages.success(request, f"Your order has been placed, estimate arrivetime is {estarrtime}!")
            # return HttpResponse("checkout successful!")
            return redirect(reverse("shopping-home"))
        elif request.POST.get("check_out"):
            print("!!!!!!!!!!!!!!checkingout!!!!!!!!!!!!!!")
            pck = package_info.objects.get(id=package_id)
            if pck.status != "":
                messages.warning(request, "You have already placed this order, do not repeat placing it!")
                return redirect(reverse("shopping-home"))
            pck.dest_x = request.POST.get("dest_x")
            pck.dest_y = request.POST.get("dest_y")
            pck.ups_account = request.POST.get("ups_account")
            pck.status = "created"
            pck.save()
            print("8888888888888888"+str(type(pck.dest_x)))
            wh_id = match_warehouse(int(pck.dest_x), int(pck.dest_y))
            pck.from_wh = warehouse.objects.get(id=wh_id)
            #makeup offset from EST to EDT
            offset = timedelta(hours=1)
            pck.package_job_time = pck.package_job_time + offset
            #update the arrival time
            d = timedelta(hours=estimateArrtime(pck))
            pck.estimate_arrtime = pck.estimate_arrtime + offset + d
            pck.save()
            buyandpack(package_id)
            sendemail(pck)
            estarrtime = str(pck.estimate_arrtime)
            messages.success(request, f"Your order has been placed, estimate arrivetime is {estarrtime}!")
            #turn to the checkout successful page!
            return redirect(reverse("shopping-home"))
    elif pck.is_gift:
        context = {
            "blessing" : pck.blessing,
        }
        return render(request, "shopping/giftcheckout_page.html", context)
    else:
        return render(request, "shopping/checkout_page.html")

def estimateArrtime(pck):
    wh = pck.from_wh
    x = int(pck.dest_x)
    y = int(pck.dest_y)
    dist = math.sqrt(math.pow(int(wh.pos_x) - x, 2) + math.pow(int(wh.pos_y) - y, 2))
    num_items=pck.order_set.count()
    print("num_items in this package is" + str(num_items))
    est_hours = dist/(700/24) + num_items * 6
    print("Est_transfer time is: " + str(est_hours))
    return int(est_hours)

def sendemail(pck):
    subject = 'Your order has been placed!'
    message = pck.info() + 'Estimate arriving time is: ' + str(pck.estimate_arrtime.strftime('%Y-%m-%d %H:%M'))+ '\n' + 'Thank you for choosing us!' 
    email_from = settings.EMAIL_HOST_USER
    recipient_list1 = [pck.owner.email]
    send_mail(subject,message,email_from,recipient_list1)

def send_advanced_email(pck):
    message = EmailMultiAlternatives(
        subject='Your order has been placed!',
        body=pck.info() + 'Thank you for choosing us!',
        from_email=settings.EMAIL_HOST_USER,
        to=[pck.owner.email],
    )
    message.mixed_subtype = 'related'
    #message.attach_alternative(body_html, "text/html")
    message.attach(logo_data())

    message.send(fail_silently=False)

@lru_cache()
def logo_data():
    with open(finders.find('templates/mail.jpeg'), 'rb') as f:
        logo_data = f.read()
    logo = MIMEImage(logo_data)
    logo.add_header('Content-ID', '<logo>')
    return logo

def toSearchResult(request):
    if request.method == "POST":
        keyword=""
        if request.POST.get("keyword"):
            keyword=request.POST["keyword"]
            return redirect(reverse("SearchResult", kwargs={'pk': keyword}))
        else:
            return redirect(reverse("shopping-home"))
    else:
        return HttpResponse("not working")

def mainpage(request):
    catas = catalog.objects.all
    # commodities = commodity.objects.filter(commodity_name__icontains='ip')
    #commodities = commodity.objects.order_by('?')[:3]
    commodities = commodity.objects.annotate(num_orders=Count('order')).order_by('-num_orders')[:3]
    context = {
        'catas' : catas,
        'commodities' : commodities,
    }
    return render(request, "shopping/mainpage.html", context)