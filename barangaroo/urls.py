"""barangaroo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.urls import path, re_path
from dashboard import views

from django.views.static import serve
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", view=views.home, name="Home"),
    path("dashboard/", view=views.ems_dashboard, name='ems_dashboard'),
    path("ems/", view=views.ems, name="ems"),
    path('water/', view=views.water, name="water"),
    path('thermal/', view=views.thermal, name='thermal'),
    path("gas/", view=views.gas, name="gas"),
    path("mater_page/", view=views.meter_page, name="meterPage"),
    path("thermal_comfort/", view=views.thermal_comfort, name="thermalComfort"),
    path("thermal_comfort_humidity/", view=views.thermal_comfort_humidity, name="thermalComfortHumidity"),
    path("thermal_comfort_co2", view=views.thermal_comfort_co2, name="thermalComfortCo2"),
    path("carpark/", view=views.car_park, name="carPark"),
    path("ev_charging", view=views.ev_charging, name="evCharging"),
    
    re_path(r'^media/(?P<path>.*)$', serve,{'document_root':       settings.MEDIA_ROOT}), 
    re_path(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),   
]