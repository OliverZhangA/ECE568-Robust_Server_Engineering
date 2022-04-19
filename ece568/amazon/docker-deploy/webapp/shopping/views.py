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
            #buyandpack(package.id)
            #return HttpResponse("buy successful")
            return redirect(reverse("checkoutpage", kwargs={'package_id': package.id}))
        else:
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
            #delete the package
            print("!!!!!!!!!!!!!!canceling!!!!!!!!!!!!!!")
            return redirect(reverse("shoppingCart"))
            #return HttpResponse("cancel checkout!!")
        elif request.POST.get("check_out"):
            print("!!!!!!!!!!!!!!checkingout!!!!!!!!!!!!!!")
            pck = package_info.objects.get(id=package_id)
            pck.dest_x = request.POST.get("dest_x")
            pck.dest_y = request.POST.get("dest_y")
            pck.ups_account = request.POST.get("ups_account")
            pck.save()
            buyandpack(package_id)
            #turn to the checkout successful page!
            return HttpResponse("checkout successful!")
    return render(request, "shopping/checkout_page.html")

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