from django.urls import path

from shopping.models import commodity
from . import views as shop_views
from .views import (
    CataDetail,
    commodityDetail,
)
#from .views import OrderDetail, OrderList
# from .views import (
#     SharerDelete,
#     OrderDelete,
#     OrderDetail, 
#     OrderList, 
#     OrderCreate,
#     OrderUpdate,
#     ShareOrderCreate,
#     ShareList,
#     ShareOrderDetail,
#     DriverList,
#     DriverConfirmDetail,
#     DriverOrderList,
#     DriverOrderDetail,
#     ShareOrderList,
#     ShareHistoryDetail,
# )

urlpatterns = [
    ## home page
    path('', shop_views.CatelogList.as_view(), name='shopping-home'),
    path('<str:pk>/', CataDetail.as_view(), name='catadetail'),
    path('commodityDetail/<int:pk1>/', shop_views.commodityDetail, name='commoditydetail'),
    path('shopping cart', shop_views.shoppingCart, name='shoppingCart'),
    path('checkout/<int:package_id>', shop_views.checkoutpage, name="checkoutpage"),
    # ## owner pages
    # path('rideuser/', views.userhome, name='ride-user'),
    # path('rideuser/riderequest/', OrderCreate.as_view(), name='ride-request'),
    # path('rideuser/ridehistory', OrderList.as_view(), name='orderlist'),
    # path('rideuser/ridehistory/<int:pk>/', OrderDetail.as_view(), name='orderdetail'),
    # path('rideuser/ridehistory/<int:pk>/update', OrderUpdate.as_view(), name='ride-update'),
    # ##delete
    # path('rideuser/ridehistory/<int:pk>/delete', OrderDelete.as_view(), name='ride-delete'),
    # ## sharer pages, request
    # path('rideuser/joinride/', ShareOrderCreate.as_view(), name='ride-join'),
    # path('rideuser/joinresults', ShareList.as_view(), name='joinlist'),
    # path('rideuser/joinresults/<int:pk>/', ShareOrderDetail.as_view(), name='shareorderdetail'),
    # path('rideuser/joinresults/<int:order_id>/confirm', views.joinconfirm, name='joinconfirm'),
    # ## edit sharer info
    # path('rideuser/joinorders/', ShareOrderList.as_view(), name='joinorders'),
    # path('rideuser/joinorders/<int:pk>/', ShareHistoryDetail.as_view(), name='joinhistory'),
    # ##delete ride sharer
    # path('rideuser/joinorders/<int:pk>/delete', SharerDelete.as_view(), name='deletesharer'),

    # #path('rideuser/joinresults/<int:pk>/return_to', ShareOrderDetail.as_view(), name='shareorderdetail'),
    # path('sharer/', views.sharer, name='ride-sharer'),

    # ## driver pages
    # path('driver/', views.driver, name='ride-driver'),
    # path('driver/driverhome', views.driverhome, name='driver-home'),
    # path('driver/driverorderlist', DriverOrderList.as_view(), name='driverorderlist'),
    # path('driver/driverorderlist/<int:pk>/', DriverOrderDetail.as_view(), name='driverorderdetail'),
    # path('driver/driverorderlist/<int:order_id>/complete', views.DriverComplete, name='drivercomplete'),

    # path('driver/driver_search_results', DriverList.as_view(), name='takeorders'),
    # path('driver_search_results/<int:pk>/', DriverConfirmDetail.as_view(), name='driverdetail'),
    # path('driver_search_results/<int:order_id>/confirm', views.DriverConfirm, name='driverconfirm'),
]

