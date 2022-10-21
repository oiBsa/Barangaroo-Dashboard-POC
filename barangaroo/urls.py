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
    path("login/", view=views.login_view, name="login"),
    path("accounts/login/", view=views.login_view, name="login"),
    path("", view=views.home, name="home"),
    path("dashboard/", view=views.ems_dashboard, name='ems_dashboard'),
    path("ems/", view=views.ems, name="ems"),
    path('water/', view=views.water, name="water"),
    path('thermal/', view=views.thermal, name='thermal'),
    path("gas/", view=views.gas, name="gas"),
    path('nabers/', view=views.nabers, name='nabers'),
    path('nabers_2/', view=views.nabers_new, name='nabers_new'),
    path("mater_page/", view=views.meter_page, name="meterPage"),
    path("thermal_comfort/", view=views.thermal_comfort, name="thermalComfort"),
    path("thermal_comfort_humidity/", view=views.thermal_comfort_humidity, name="thermalComfortHumidity"),
    path("thermal_comfort_co2", view=views.thermal_comfort_co2, name="thermalComfortCo2"),
    path("carpark/", view=views.car_park, name="carPark"),
    path("carpark_summary/", view=views.car_park_page, name="carparkSummary"),
    path("ev_charging/", view=views.ev_charging, name="evCharging"),
    path("ev_charging_cost_per_charge/", view=views.ev_cost_per_charge, name='EV_CPC'),
    path("ev_charging_avg_energy_per_charge/", view=views.ev_avg_eng_per_charge, name="EV_AEPC"),
    path("ev_charging_emission_reduction/", view=views.ev_charging_emission_reduction, name="EV_ER"),
    path("weather_forcast/", view=views.weather_forcast, name="weather"),
    
    re_path(r'^media/(?P<path>.*)$', serve,{'document_root':       settings.MEDIA_ROOT}), 
    re_path(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),   
]