from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def home(request):
    return HttpResponse('<h1>Ride Home</h1>')

def owner(request):
    return HttpResponse('<h1>Ride Owner Home</h1>')

def sharer(request):
    return HttpResponse('<h1>Ride Sharer Home</h1>')

def driver(request):
    return HttpResponse('<h1>Ride Driver Home</h1>')

