from itertools import product
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import catalog, commodity, package_info
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
        context['commo'] = commo
        return render(request, "shopping/commoditydetail.html", context)