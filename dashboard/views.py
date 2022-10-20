
import re
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.urls import reverse

# Create your views here.
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm()
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request=request, username=username, password=password)
        if user is not None: 
            login(request=request, user=user)
            return render(request=request, template_name="home.html")
        else: return render(request=request, template_name="login.html", context={'form':form})
    else:
        form = AuthenticationForm()
    return render(request=request, template_name="login.html", context={'form':form})

@login_required(login_url='/login/')
def home(request):
    return render(request=request, template_name="home.html")

def ems_dashboard(request):
    if request.user.is_authenticated: return render(request=request, template_name="index.html")
    else: return redirect("home")

def ems(request):
    if request.user.is_authenticated: return render(request=request, template_name="EMS.html")
    else: return redirect("home")

def water(request):
    if request.user.is_authenticated: return render(request=request, template_name="WATER.html")
    else: return redirect("home")
    
def thermal(request):
    if request.user.is_authenticated: return render(request=request, template_name="THERMAL.html")
    else: return redirect("home")

def gas(request):
    if request.user.is_authenticated: return render(request=request, template_name="GAS.html")
    else: return redirect("home")
    
def nabers(request):
    if request.user.is_authenticated: return render(request=request, template_name="nabers.html")
    else: return redirect("home")

def nabers_new(request):
    if request.user.is_authenticated: return render(request=request, template_name="nabers_new.html")
    else: return redirect("home")


def meter_page(request):
    if request.user.is_authenticated: return render(request=request, template_name="EQUIP.html")
    else: return redirect("home")

def thermal_comfort(request):
    if request.user.is_authenticated: return render(request=request, template_name="ThermalComfortDashboard.html")
    else: return redirect("home")

def thermal_comfort_humidity(request):
    if request.user.is_authenticated: return render(request=request, template_name="ThermalComfortHumidity.html")
    else: return redirect("home")

def thermal_comfort_co2(request):
    if request.user.is_authenticated: return render(request=request, template_name="ThermalComfortCO2.html")
    else: return redirect("home")

def car_park(request):
    if request.user.is_authenticated: return render(request=request, template_name="CarPark.html")
    else: return redirect("home")

def car_park_page(request):
    if request.user.is_authenticated: return render(request=request, template_name="CarParkSummary.html")
    else: return redirect("home")

def ev_charging(request):
    if request.user.is_authenticated: return render(request=request, template_name="EVCharging_new.html")
    else: return redirect("home")
    
def ev_cost_per_charge(request):
    if request.user.is_authenticated: return render(request=request, template_name="EVChargingCostPerCharge.html")
    else: return redirect("home")

def ev_avg_eng_per_charge(request):
    if request.user.is_authenticated: return render(request=request, template_name="EVChargingAvgEngPerCharge.html")
    else: return redirect("home")

def ev_charging_emission_reduction(request):
    if request.user.is_authenticated: return render(request=request, template_name="EVChargingEmissionReduction.html")
    else: return redirect("home")