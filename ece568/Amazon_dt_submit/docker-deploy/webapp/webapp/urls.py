"""webapp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from users import views as user_views
from django.urls import include
from django.conf import settings
from django.conf.urls.static import static
from shopping import views as shop_views

urlpatterns = [
    path('driverprofile/', user_views.driverform, name='driverprofile'),
    path('register/', user_views.register, name='register'),

    #path('rideuser/ridehistory', OrderList.as_view(), name='orderlist'),
    path('catalog/', include('shopping.urls')),
    #path('catalog/', shop_views.CatelogList.as_view(), name='shopping-home'),

    path('catalog/', shop_views.CatelogList.as_view(), name='ride-user'),
    path('catalog/', shop_views.CatelogList.as_view(), name='ride-driver'),

    path('admin/', admin.site.urls),
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('', shop_views.mainpage, name='mainpage')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
