
from django.shortcuts import render

# Create your views here.

def home(request):
    return render(request=request, template_name="home.html")

def ems_dashboard(request):
    return render(request=request, template_name="index.html")

def ems(request):
    return render(request=request, template_name="EMS.html")

def water(request):
    return render(request=request, template_name="WATER.html")

def thermal(request):
    return render(request=request, template_name="THERMAL.html")

def gas(request):
    return render(request=request, template_name="GAS.html")

def meter_page(request):
    return render(request=request, template_name="EQUIP.html")

def thermal_comfort(request):
    return render(request=request, template_name="ThermalComfortDashboard.html")

def thermal_comfort_humidity(request):
    return render(request=request, template_name="ThermalComfortHumidity.html")

def thermal_comfort_co2(request):
    return render(request=request, template_name="ThermalComfortCO2.html")

def car_park(request):
    return render(request=request, template_name="CarPark.html")

def ev_charging(request):
    return render(request=request, template_name="EVCharging.html")