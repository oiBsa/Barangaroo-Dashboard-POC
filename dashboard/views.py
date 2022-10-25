
import re
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.urls import reverse
import pymssql
from datetime import datetime
import json, requests

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
    print(check_ofline)
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
    results = requests.get("http://api.openweathermap.org/data/2.5/forecast?id=2147714&units=metric&appid=c394c5e0aec171094aa6e1083e1e40e1").json()
    current_datetime = datetime.now()
    for cuurent_weather_data in results['list']:
        date_varialble = datetime.strptime(cuurent_weather_data["dt_txt"], "%Y-%m-%d %H:%M:%S")
        starting_weekday = date_varialble.weekday()
        starting_date = date_varialble.date()
        if abs((current_datetime - date_varialble).total_seconds())<5400: break
    print(str(starting_date.strftime("%b")).upper())
    data = {"0":{"temp":cuurent_weather_data["main"]["temp"], "feels_like":cuurent_weather_data["main"]["feels_like"], "pressure":cuurent_weather_data["main"]["pressure"]/1000,
        "humidity":cuurent_weather_data["main"]["humidity"], "status":cuurent_weather_data["weather"][0]["main"], "icon":cuurent_weather_data["weather"][0]["icon"], "wind_speed":cuurent_weather_data["wind"]["speed"],
        "wind_direction":cuurent_weather_data["wind"]["deg"], "vision":cuurent_weather_data["visibility"]/1000, "day":f"{starting_weekday}", "date":starting_date.day, "month":str(starting_date.strftime("%b")).upper()},
    "1":{"temp":results['list'][8]["main"]["temp"], "feels_like":results['list'][8]["main"]["feels_like"], "pressure":results['list'][8]["main"]["pressure"]/1000,
        "humidity":results['list'][8]["main"]["humidity"], "status":results['list'][8]["weather"][0]["main"], "icon":results['list'][8]["weather"][0]["icon"], "wind_speed":results['list'][8]["wind"]["speed"],
        "wind_direction":results['list'][8]["wind"]["deg"], "vision":results['list'][8]["visibility"]/1000, "day":f"{starting_weekday+1}", "date":str(starting_date.day)},
    "2":{"temp":results['list'][16]["main"]["temp"], "feels_like":results['list'][16]["main"]["feels_like"], "pressure":results['list'][16]["main"]["pressure"]/1000,
        "humidity":results['list'][16]["main"]["humidity"], "status":results['list'][16]["weather"][0]["main"], "icon":results['list'][16]["weather"][0]["icon"], "wind_speed":results['list'][16]["wind"]["speed"],
        "wind_direction":results['list'][16]["wind"]["deg"], "vision":results['list'][16]["visibility"]/1000,"day":f"{starting_weekday+2}"},
    "3":{"temp":results['list'][24]["main"]["temp"], "feels_like":results['list'][24]["main"]["feels_like"], "pressure":results['list'][24]["main"]["pressure"]/1000,
        "humidity":results['list'][24]["main"]["humidity"], "status":results['list'][24]["weather"][0]["main"], "icon":results['list'][24]["weather"][0]["icon"], "wind_speed":results['list'][24]["wind"]["speed"],
        "wind_direction":results['list'][24]["wind"]["deg"], "vision":results['list'][24]["visibility"]/1000, "day":f"{starting_weekday+3}"},
    "4":{"temp":results['list'][32]["main"]["temp"], "feels_like":results['list'][32]["main"]["feels_like"], "pressure":results['list'][32]["main"]["pressure"]/1000,
        "humidity":results['list'][32]["main"]["humidity"], "status":results['list'][32]["weather"][0]["main"], "icon":results['list'][32]["weather"][0]["icon"], "wind_speed":results['list'][32]["wind"]["speed"],
        "wind_direction":results['list'][32]["wind"]["deg"], "vision":results['list'][32]["visibility"]/1000,"day":f"{starting_weekday+4}"}}
    return render(request=request, template_name="weatherForcast.html", context={"weather":data})