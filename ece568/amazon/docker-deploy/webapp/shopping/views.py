from itertools import product
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import catalog, commodity, order, package_info
from django.shortcuts import render, redirect
from django.urls import reverse
from .functions import buyandpack


# Create your views here.
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

# class commodityDetail(DetailView):
#     model = commodity
#     template_name = 'shopping/commoditydetail.html'

def commodityDetail(request, pk1):
    commo = commodity.objects.get(pk=pk1)
    context = {
        'commodity' : 'commo'
    }
    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect(reverse("login"))
        amount = int(request.POST["count"])
        if request.POST["action"] == "buy":
            # create a new package
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
            buyandpack(package.id)
            return HttpResponse("buy successful")
            #return redirect(reverse("checkout", kwargs={'package_id': package.id}))
        else:
            #try to adding the item to cart
            #check if there is existing cart
            # order_in_cart = None
            # order_in_cart = order.objects.get(owner=request.user, commodity=commo, package_info__isnull=True)
            # #already in the cart
            # if(order_in_cart != None):
            #     order_in_cart.commodity_amt += amount
            #     order_in_cart.save()
            # #not in the cart
            # else:
            #     neworder = order(owner=request.user, commodity=commo, commodity_amt=amount)
            #     neworder.save()
            #     context = {
            #         "prompt" : "Adding to cart successfully"
            #     }
            #     return render(request, "sucToCart.html", context)
            try:
                order_in_cart = order.objects.get(owner=request.user, commodity=commo, package_info__isnull=True)
                order_in_cart.commodity_amt += amount
                order_in_cart.save()
            except order.DoesNotExist:
                neworder = order(owner=request.user, commodity=commo, commodity_amt=amount)
                neworder.save()
            context = {
                "prompt" : "Adding to cart successfully"
            }
            return render(request, "shopping/sucToCart.html", context)

    else:
        context['commo'] = commo
        return render(request, "shopping/commoditydetail.html", context)

def shoppingCart(request):
    orders = order.objects.filter(owner=request.user).filter(package_info__isnull=True).order_by("order_time")
    if request.method == "POST":
        op = request.POST["op"]
        if op == "delete":
            orderid = request.POST["order_id"]
            orders.get(pk=orderid).delete()
        #case that op is checkout
        else:
            pck = package_info(owner=request.user)
            for ord in orders:
                ord.package_info = pck
                ord.save()
            return redirect(reverse("checkout", kwargs={'package_id': pck.id}))
    context = {"orders": orders}
    return render(request, "shopping/shopping_cart.html", context)

