
import re
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.urls import reverse
import pymssql
from datetime import datetime
import json

QUERY_get_ems = '''use [barangaroo]

	SELECT	IPLV.PointKey AS PointKey,
			AM.AssetID,
			IPT.PointTemplateName,
			IPLV.PointValue,
			IPLV.LastReceivedTime,
			AM.Description,
			IPS.IsOnline

	FROM IBMSPointLastValues IPLV
		INNER JOIN IBMSPoints IPS ON IPS.PointKey = IPLV.PointKey
		INNER JOIN IBMSPointTemplates IPT ON IPT.PointTemplateKey = IPS.PointTemplateKey
		INNER JOIN AssetMaster AM ON AM.AssetKey = IPS.AssetKey

	WHERE PointTemplateName LIKE '%Active Energy%'
	AND AssetID LIKE '%-EM-%'

	ORDER By LastReceivedTime DESC'''

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

#@login_required(login_url='/login/')
def home(request):
    return render(request=request, template_name="home.html")

def ems_dashboard(request):
    #if request.user.is_authenticated: return render(request=request, template_name="index.html")
    #else: return redirect("home")
    return render(request=request, template_name="index.html")

def ems(request):
    #if request.user.is_authenticated: return render(request=request, template_name="EMS.html")
    #else: return redirect("home")
    if request.method == 'GET': req_pointKey = request.GET.get("pointKey")
    dbhost = '10.0.65.231'
    dbuser = 'sa'
    dbpassword = 'C0mplex@1234'
    dbdatabase = 'barangaroo'
    conn = pymssql.connect(host=dbhost, user=dbuser, password=dbpassword, database=dbdatabase)
    cur = conn.cursor()
    cur.execute(QUERY_get_ems)
    result = cur.fetchall()
    cur.close()
    conn.close()
    EMS_result = []
    total_consumption = 0
    total_online = []
    total_offline = []
    for pointKey, AssetID, POintTemplateName, PointValue, LastRecievedTime, Description, IsOnline in result:
        try: 
            PointValue = int(PointValue)
            EMS_result.append([pointKey, AssetID, POintTemplateName, PointValue, LastRecievedTime, Description, IsOnline])
            total_consumption+=PointValue
            if IsOnline==1:total_online.append(AssetID)
            if IsOnline==0:total_offline.append({"AssetID":AssetID, "Last":str(LastRecievedTime.strftime("%Y-%m-%d %H:%M:%S"))})
        except: pass
    check_ofline = False
    if len(total_offline)>0:check_ofline=True
    data = {"EMS":EMS_result, "total_consumption":total_consumption, "total_online":len(total_online), "total_offline":len(total_offline), 
            "check_offline":check_ofline, "total_meters":len(total_online)+len(total_offline), "offline":total_offline}
    
    return render(request=request, template_name="EMS.html", context=data)

def water(request):
    #if request.user.is_authenticated: return render(request=request, template_name="WATER.html")
    #else: return redirect("home")
    return render(request=request, template_name="WATER.html")
    
def thermal(request):
    #if request.user.is_authenticated: return render(request=request, template_name="THERMAL.html")
    #else: return redirect("home")
    return render(request=request, template_name="THERMAL.html")

def gas(request):
    #if request.user.is_authenticated: return render(request=request, template_name="GAS.html")
    #else: return redirect("home")
    return render(request=request, template_name="GAS.html")
    
def nabers(request):
    #if request.user.is_authenticated: return render(request=request, template_name="nabers.html")
    #else: return redirect("home")
    return render(request=request, template_name="nabers.html")

def nabers_new(request):
    #if request.user.is_authenticated: return render(request=request, template_name="nabers_new.html")
    #else: return redirect("home")
    return render(request=request, template_name="nabers_new.html")


def meter_page(request):
    #if request.user.is_authenticated: return render(request=request, template_name="EQUIP.html")
    #else: return redirect("home")
    return render(request=request, template_name="EQUIP.html")

def thermal_comfort(request):
    #if request.user.is_authenticated: return render(request=request, template_name="ThermalComfortDashboard.html")
    #else: return redirect("home")
    return render(request=request, template_name="ThermalComfortDashboard.html")

def thermal_comfort_humidity(request):
    #if request.user.is_authenticated: return render(request=request, template_name="ThermalComfortHumidity.html")
    #else: return redirect("home")
    return render(request=request, template_name="ThermalComfortHumidity.html")

def thermal_comfort_co2(request):
    #if request.user.is_authenticated: return render(request=request, template_name="ThermalComfortCO2.html")
    #else: return redirect("home")
    return render(request=request, template_name="ThermalComfortCO2.html")

def car_park(request):
    #if request.user.is_authenticated: return render(request=request, template_name="CarPark.html")
    #else: return redirect("home")
    return render(request=request, template_name="CarPark.html")

def car_park_page(request):
    #if request.user.is_authenticated: return render(request=request, template_name="CarParkSummary.html")
    #else: return redirect("home")
    return render(request=request, template_name="CarParkSummary.html")

def ev_charging(request):
    #if request.user.is_authenticated: return render(request=request, template_name="EVCharging_new.html")
    #else: return redirect("home")
    return render(request=request, template_name="EVCharging_new.html")
    
def ev_cost_per_charge(request):
    #if request.user.is_authenticated: return render(request=request, template_name="EVChargingCostPerCharge.html")
    #else: return redirect("home")
    return render(request=request, template_name="EVChargingCostPerCharge.html")

def ev_avg_eng_per_charge(request):
    #if request.user.is_authenticated: return render(request=request, template_name="EVChargingAvgEngPerCharge.html")
    #else: return redirect("home")
    return render(request=request, template_name="EVChargingAvgEngPerCharge.html")

def ev_charging_emission_reduction(request):
    #if request.user.is_authenticated: return render(request=request, template_name="EVChargingEmissionReduction.html")
    #else: return redirect("home")
    return render(request=request, template_name="EVChargingEmissionReduction.html")
    
def weather_forcast(request):
    #if request.user.is_authenticated: return render(request=request, template_name="weatherForcast.html")
    #else: return redirect("home")
    return render(request=request, template_name="weatherForcast.html")