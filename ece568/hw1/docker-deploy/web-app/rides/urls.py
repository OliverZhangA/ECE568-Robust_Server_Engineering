from django.urls import path
from . import views
#from .views import OrderDetail, OrderList
from .views import (
    OrderDetail, 
    OrderList, 
    OrderCreate,
    OrderUpdate
)

urlpatterns = [
    path('', views.home, name='ride-home'),
    #path('owner/', views.owner, name='ride-owner'),
    path('rideuser/', views.userhome, name='ride-user'),
    #path('rideuser/riderequest/', views.request_ride, name='ride-request'),
    path('rideuser/ridehistory', OrderList.as_view(), name='orderlist'),
    path('rideuser/ridehistory/<int:pk>/', OrderDetail.as_view(), name='orderdetail'),
    path('rideuser/riderequest/', OrderCreate.as_view(), name='ride-request'),
    path('rideuser/<int:pk>/update', OrderUpdate.as_view(), name='ride-update'),
    path('sharer/', views.sharer, name='ride-sharer'),
    path('driver/', views.driver, name='ride-driver'),
]

