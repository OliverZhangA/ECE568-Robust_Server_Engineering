from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='ride-home'),
    path('owner/', views.owner, name='ride-owner'),
    path('sharer/', views.sharer, name='ride-sharer'),
    path('driver/', views.driver, name='ride-driver'),
]