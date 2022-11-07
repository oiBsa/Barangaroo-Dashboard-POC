import requests
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
import pymssql
from datetime import datetime, timedelta
import json, requests
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt
import pytz
import pandas as pd

DF = pd.ExcelFile("barangaroo//static//admin//file//Data.xlsx")

ABOVE_SET_POINT = 23.0
BELOW_SET_POINT = 21.0


monthly_graph = {}
weekly_graph = {}
daily_graph = {}

def get_below(lst:list, value:float): return [equip for equip in lst if equip[2]<=value]

def get_above(lst:list, value:float): return [equip for equip in lst if equip[2]>value]

def get_datetime_avg(lst:list, valuea:float, valueb:float):
    date_dict, date_dict_above, date_dict_below = {}, {}, {}
    for equip in lst:
        if equip[3] not in date_dict: date_dict[equip[3]] = []
        else: date_dict[equip[3]] = date_dict[equip[3]] + [equip[2]]
    for date_equip in date_dict:
        above_list = [equip for equip in date_dict[date_equip] if equip>valuea]
        below_list = [equip for equip in date_dict[date_equip] if equip<=valueb]
        try: date_dict_above[date_equip] = round((len(above_list)/(len(above_list)+len(below_list)))*100)
        except: date_dict_above[date_equip] = 0
        try: date_dict_below[date_equip] = round((len(below_list)/(len(above_list)+len(below_list)))*100)
        except: date_dict_below[date_equip] = 0
    return date_dict_above, date_dict_below

def get_datetime_avg_per_day(lst:list, valuea:float, valueb:float):
    date_dict, date_dict_above, date_dict_below = {}, {}, {}
    for equip in lst:
        if equip[3].date() not in date_dict: date_dict[equip[3].date()] = []
        else: date_dict[equip[3].date()] = date_dict[equip[3].date()] + [equip[2]]
    for date_equip in date_dict:
        above_list = [equip for equip in date_dict[date_equip] if equip>valuea]
        below_list = [equip for equip in date_dict[date_equip] if equip<=valueb]
        try: date_dict_above[date_equip] = round((len(above_list)/(len(above_list)+len(below_list)))*100)
        except: date_dict_above[date_equip] = 0
        try: date_dict_below[date_equip] = round((len(below_list)/(len(above_list)+len(below_list)))*100)
        except: date_dict_below[date_equip] = 0
    return date_dict_above, date_dict_below

# Create your views here

#@login_required(login_url='/login/')
def home(request):
    return render(request=request, template_name="home.html")

def ems_dashboard(request):
    #if request.user.is_authenticated: return render(request=request, template_name="index.html")
    #else: return redirect("home")
    return render(request=request, template_name="index.html")

target_meter = ""
def ems(request):
    global target_meter
    DF_EMS = DF.parse(sheet_name="EMS")
    DF_EM1 = DF.parse(sheet_name="EM1")
    DF_EM2 = DF.parse(sheet_name="EM2")
    DF_EM3 = DF.parse(sheet_name="EM3")
    DF_EM4 = DF.parse(sheet_name="EM4")
    current_datetime = datetime.utcnow() + timedelta(days=1)
    end_datetime = current_datetime - timedelta(days=31)
    current_datetime = str(current_datetime.strftime("%Y-%m-%d"))
    end_datetime = str(end_datetime.strftime("%Y-%m-%d"))
    
    #if request.user.is_authenticated: return render(request=request, template_name="EMS.html")
    #else: return redirect("home")
    if request.method == 'GET': 
        req_pointKey = request.GET.get("pointKey")
        graphStartDate = request.GET.get("graphStartDate")
        graphEndDate = request.GET.get("graphEndDate")
    if req_pointKey!=None:
        monthly_graph = {}
        weekly_graph = {}
        daily_graph = {}
        if req_pointKey=="249782": graph_results = DF_EM1.values.tolist()
        elif req_pointKey=="120587": graph_results = DF_EM2.values.tolist()
        elif req_pointKey=="120923": graph_results = DF_EM3.values.tolist()
        else: graph_results = DF_EM4.values.tolist()
        monthly = {}
        for equip in graph_results:
            current_date = str(equip[-1]).split(" ")[0]
            consumption = []
            for dummy_equip in graph_results:
                if current_date in str(dummy_equip[-1]): consumption.append(dummy_equip[2])
            monthly[current_date] = consumption[-1]
        weekly = {k: monthly[k] for k in list(monthly)[-7:]}
        daily = {str(k[-1]).split(":")[0]:k[2] for k in graph_results[-24:]}
        monthly_graph = {"x":[m for m in monthly.keys()], "y":[n for n in monthly.values()]}
        weekly_graph = {"x":[m for m in weekly.keys()], "y":[n for n in weekly.values()]}
        daily_graph = {"x":[m for m in daily.keys()], "y":[n for n in daily.values()]}
        target_meter = req_pointKey
        print(monthly)
        return JsonResponse({"monthly":monthly_graph, "weekly":weekly_graph, "daily":daily_graph}, status=200)
    else:
        result = DF_EMS.values.tolist()
        graph_ponts = {"x":[], "y":[]}
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
        EMS_result = sorted(EMS_result, key=lambda t: t[3], reverse=True)
        graph_ponts["x"] = [AssetID for pointKey, AssetID, POintTemplateName, PointValue, LastRecievedTime, Description, IsOnline in EMS_result[:30]]
        graph_ponts["y"] = [pointKey for pointKey, AssetID, POintTemplateName, PointValue, LastRecievedTime, Description, IsOnline in EMS_result[:30]]
        
        return render(request=request, template_name="EMS.html", context={"EMS":EMS_result, "total_consumption":total_consumption, "total_online":len(total_online), "total_offline":len(total_offline), 
            "check_offline":check_ofline, "total_meters":len(total_online)+len(total_offline), "offline":total_offline, "graphPoints":graph_ponts})

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

@xframe_options_exempt
@csrf_exempt
def thermal_comfort(request):
    #if request.user.is_authenticated: return render(request=request, template_name="ThermalComfortDashboard.html")
    #else: return redirect("home")
    DF_THERMAL = DF.parse(sheet_name="THERMAL")
    DF_THERMAL_LEVEL1 = DF.parse(sheet_name="THERMAL_LEVEL1")
    DF_THERMAL_LEVEL2 = DF.parse(sheet_name="THERMAL_LEVEL2")
    DF_THERMAL_LEVEL3 = DF.parse(sheet_name="THERMAL_LEVEL3")
    DF_THERMAL_LEVEL4 = DF.parse(sheet_name="THERMAL_LEVEL4")
    if request.method == 'GET': 
        req_tower = request.GET.get("tower")
        req_level = request.GET.get("level")
    if req_tower!=None:
        req_tower = int(req_tower)
        if req_level=="00": level_1 = DF_THERMAL_LEVEL1.values.tolist()
        elif req_level=="01": level_1 = DF_THERMAL_LEVEL2.values.tolist()
        elif req_level=="02": level_1 = DF_THERMAL_LEVEL3.values.tolist()
        else: level_1 = DF_THERMAL_LEVEL4.values.tolist()
        
        level_1_above = [equip for equip in level_1 if equip[2]>ABOVE_SET_POINT]
        level_1_below = [equip for equip in level_1 if equip[2]<=ABOVE_SET_POINT]
        above_avg = round((len(level_1_above)/len(level_1))*100)
        below_avg = round((len(level_1_below)/len(level_1))*100)
        above_temp_avg = round(sum([equip[2] for equip in level_1_above])/len(level_1_above), 1)
        below_temp_avg = round(sum([equip[2] for equip in level_1_below])/len(level_1_below), 1)
        above_date_percent, below_date_percent = get_datetime_avg(lst=level_1, valuea=ABOVE_SET_POINT, valueb=BELOW_SET_POINT)
        above_date_percent_per_day, below_date_percent_per_day = get_datetime_avg_per_day(lst=level_1, valuea=ABOVE_SET_POINT, valueb=BELOW_SET_POINT)
        last_date = list(above_date_percent.keys())[0]
        daily_above = [i for i in above_date_percent.items() if str(i[0].date())==str(last_date.date())]
        daily_below = [i for i in below_date_percent.items() if str(i[0].date())==str(last_date.date())]
        weekly_above = [i for i in above_date_percent_per_day.items() if str(i[0].strftime("%V"))==str(last_date.strftime("%V"))]
        weekly_below = [i for i in below_date_percent_per_day.items() if str(i[0].strftime("%V"))==str(last_date.strftime("%V"))]
        monthly_above = [i for i in above_date_percent_per_day.items() if str(i[0].strftime("%m"))==str(last_date.strftime("%m"))]
        monthly_below = [i for i in below_date_percent_per_day.items() if str(i[0].strftime("%m"))==str(last_date.strftime("%m"))]
        dailyAboveGraph = {"x":[str(i[0].strftime("%H:%M")) for i in daily_above], "y":[i[1] for i in daily_above]}
        dailyBelowGraph = {"x":[str(i[0].strftime("%H:%M")) for i in daily_below], "y":[i[1] for i in daily_below]}
        weeklyAboveGraph = {"x":[str(i[0]) for i in weekly_above], "y":[str(i[1]) for i in weekly_above]}
        weeklyBelowGraph = {"x":[str(i[0]) for i in weekly_below], "y":[str(i[1]) for i in weekly_below]}
        monthlyAboveGraph = {"x":[str(i[0]) for i in monthly_above], "y":[str(i[1]) for i in monthly_above]}
        monthlyBelowGraph = {"x":[str(i[0]) for i in monthly_below], "y":[str(i[1]) for i in monthly_below]}
        graphPoints = {"daily":{"above":dailyAboveGraph, "below":dailyBelowGraph},
                       "weekly":{"above":weeklyAboveGraph, "below":weeklyBelowGraph},
                       "monthly":{"above":monthlyAboveGraph, "below":monthlyBelowGraph}}
        return JsonResponse({"aboveAvg":above_avg, "belowAvg":below_avg, "aboveThresh":ABOVE_SET_POINT, "belowThresh":BELOW_SET_POINT, 
                             "aboveTempAvg":above_temp_avg, "belowTempAvg":below_temp_avg, "graphPoints":graphPoints})
    else:
        all_thermal_equip = DF_THERMAL.values.tolist()
        level_1 = DF_THERMAL_LEVEL1.values.tolist()
        level_1_above = [equip for equip in level_1 if equip[2]>ABOVE_SET_POINT]
        level_1_below = [equip for equip in level_1 if equip[2]<=ABOVE_SET_POINT]
        above_avg = round((len(level_1_above)/len(level_1))*100)
        below_avg = round((len(level_1_below)/len(level_1))*100)
        above_temp_avg = round(sum([equip[2] for equip in level_1_above])/len(level_1_above), 1)
        below_temp_avg = round(sum([equip[2] for equip in level_1_below])/len(level_1_below), 1)
        above_date_percent, below_date_percent = get_datetime_avg(lst=level_1, valuea=ABOVE_SET_POINT, valueb=BELOW_SET_POINT)
        above_date_percent_per_day, below_date_percent_per_day = get_datetime_avg_per_day(lst=level_1, valuea=ABOVE_SET_POINT, valueb=BELOW_SET_POINT)
        last_date = list(above_date_percent.keys())[0]
        daily_above = [i for i in above_date_percent.items() if str(i[0].date())==str(last_date.date())]
        daily_below = [i for i in below_date_percent.items() if str(i[0].date())==str(last_date.date())]
        weekly_above = [i for i in above_date_percent_per_day.items() if str(i[0].strftime("%V"))==str(last_date.strftime("%V"))]
        weekly_below = [i for i in below_date_percent_per_day.items() if str(i[0].strftime("%V"))==str(last_date.strftime("%V"))]
        monthly_above = [i for i in above_date_percent_per_day.items() if str(i[0].strftime("%m"))==str(last_date.strftime("%m"))]
        monthly_below = [i for i in below_date_percent_per_day.items() if str(i[0].strftime("%m"))==str(last_date.strftime("%m"))]
        dailyAboveGraph = {"x":[str(i[0].strftime("%H:%M")) for i in daily_above], "y":[i[1] for i in daily_above]}
        dailyBelowGraph = {"x":[str(i[0].strftime("%H:%M")) for i in daily_below], "y":[i[1] for i in daily_below]}
        weeklyAboveGraph = {"x":[str(i[0]) for i in weekly_above], "y":[str(i[1]) for i in weekly_above]}
        weeklyBelowGraph = {"x":[str(i[0]) for i in weekly_below], "y":[str(i[1]) for i in weekly_below]}
        monthlyAboveGraph = {"x":[str(i[0]) for i in monthly_above], "y":[str(i[1]) for i in monthly_above]}
        monthlyBelowGraph = {"x":[str(i[0]) for i in monthly_below], "y":[str(i[1]) for i in monthly_below]}
        dailyAboveEquip = [{"equip":equip[0], "temp":equip[2], "time":str(equip[-1])} for equip in level_1 if ((str(equip[-1].date())==str(last_date.date())) and (equip[2]>ABOVE_SET_POINT))]
        dailyBelowEquip = [{"equip":equip[0], "temp":equip[2], "time":str(equip[-1])} for equip in level_1 if ((str(equip[-1].date())==str(last_date.date())) and (equip[2]<=ABOVE_SET_POINT))]
        weeklyAboveEquip = [{"equip":equip[0], "temp":equip[2], "time":str(equip[-1])} for equip in level_1 if ((str(equip[-1].strftime("%V"))==str(last_date.strftime("%V"))) and (equip[2]>ABOVE_SET_POINT))]
        weeklyBelowEquip = [{"equip":equip[0], "temp":equip[2], "time":str(equip[-1])} for equip in level_1 if ((str(equip[-1].strftime("%V"))==str(last_date.strftime("%V"))) and (equip[2]<=ABOVE_SET_POINT))]
        monthlyAboveEquip = [{"equip":equip[0], "temp":equip[2], "time":str(equip[-1])} for equip in level_1 if ((str(equip[-1].strftime("%m"))==str(last_date.strftime("%m"))) and (equip[2]>ABOVE_SET_POINT))]
        monthlyBelowEquip = [{"equip":equip[0], "temp":equip[2], "time":str(equip[-1])} for equip in level_1 if ((str(equip[-1].strftime("%m"))==str(last_date.strftime("%m"))) and (equip[2]<=ABOVE_SET_POINT))]
        
        EQUIPPOINTS = {"daily":{"above":dailyAboveEquip, "below":dailyBelowEquip},
                       "weekly":{"above":weeklyAboveEquip, "below":weeklyBelowEquip},
                       "monthly":{"above":monthlyAboveEquip, "below":monthlyBelowEquip}}
        graphPoints = {"daily":{"above":dailyAboveGraph, "below":dailyBelowGraph},
                       "weekly":{"above":weeklyAboveGraph, "below":weeklyBelowGraph},
                       "monthly":{"above":monthlyAboveGraph, "below":monthlyBelowGraph}}
        
        THERMAL_DATA = [[e[0], e[1], round(float(e[3]), 1)] for e in all_thermal_equip]
        thermal_towers = {"tower1":{"equip":[], "levels":[]},"tower2":{"equip":[], "levels":[]}, "tower3":{"equip":[], "levels":[]}}
        for EQUIP in THERMAL_DATA:
            if EQUIP[1].split("-")[0][-1]=="3":
                thermal_towers["tower1"]["equip"].append(EQUIP[:2])
                thermal_towers["tower1"]["levels"].append(EQUIP[1].split("-")[1])
            elif EQUIP[1].split("-")[0][-1]=="4":
                thermal_towers["tower2"]["equip"].append(EQUIP[:2])
                thermal_towers["tower2"]["levels"].append(EQUIP[1].split("-")[1])
            elif EQUIP[1].split("-")[0][-1]=="5":
                thermal_towers["tower3"]["equip"].append(EQUIP[:2])
                thermal_towers["tower3"]["levels"].append(EQUIP[1].split("-")[1])
        thermal_towers["tower1"]["levels"] = sorted(list(set(thermal_towers["tower1"]["levels"])), reverse=False)
        thermal_towers["tower2"]["levels"] = sorted(list(set(thermal_towers["tower2"]["levels"])), reverse=False)
        thermal_towers["tower3"]["levels"] = sorted(list(set(thermal_towers["tower3"]["levels"])), reverse=False)
        return render(request=request, template_name="ThermalComfortDashboard.html", context={"THERMAL":thermal_towers, "aboveAvg":above_avg, "belowAvg":below_avg, 
                                                        "aboveThresh":ABOVE_SET_POINT, "belowThresh":BELOW_SET_POINT, "aboveTempAvg":above_temp_avg, "belowTempAvg":below_temp_avg,
                                                        "graphPoints":graphPoints, "EQUIP":EQUIPPOINTS})

def thermal_comfort_humidity(request):
    #if request.user.is_authenticated: return render(request=request, template_name="ThermalComfortHumidity.html")
    #else: return redirect("home")
    return render(request=request, template_name="ThermalComfortHumidity.html")

def thermal_comfort_co2(request):
    #if request.user.is_authenticated: return render(request=request, template_name="ThermalComfortCO2.html")
    #else: return redirect("home")
    DF_THERMAL = DF.parse(sheet_name="THERMAL")
    DF_THERMAL_LEVEL1 = DF.parse(sheet_name="THERMAL_LEVEL1")
    all_thermal_equip = DF_THERMAL.values.tolist()
    level_1 = DF_THERMAL_LEVEL1.values.tolist()
    level_1_above = [equip for equip in level_1 if equip[2]>ABOVE_SET_POINT]
    level_1_below = [equip for equip in level_1 if equip[2]<=ABOVE_SET_POINT]
    above_avg = round((len(level_1_above)/len(level_1))*100)
    below_avg = round((len(level_1_below)/len(level_1))*100)
    above_temp_avg = round(sum([equip[2] for equip in level_1_above])/len(level_1_above), 1)
    below_temp_avg = round(sum([equip[2] for equip in level_1_below])/len(level_1_below), 1)
    above_date_percent, below_date_percent = get_datetime_avg(lst=level_1, valuea=ABOVE_SET_POINT, valueb=BELOW_SET_POINT)
    above_date_percent_per_day, below_date_percent_per_day = get_datetime_avg_per_day(lst=level_1, valuea=ABOVE_SET_POINT, valueb=BELOW_SET_POINT)
    last_date = list(above_date_percent.keys())[0]
    daily_above = [i for i in above_date_percent.items() if str(i[0].date())==str(last_date.date())]
    daily_below = [i for i in below_date_percent.items() if str(i[0].date())==str(last_date.date())]
    weekly_above = [i for i in above_date_percent_per_day.items() if str(i[0].strftime("%V"))==str(last_date.strftime("%V"))]
    weekly_below = [i for i in below_date_percent_per_day.items() if str(i[0].strftime("%V"))==str(last_date.strftime("%V"))]
    monthly_above = [i for i in above_date_percent_per_day.items() if str(i[0].strftime("%m"))==str(last_date.strftime("%m"))]
    monthly_below = [i for i in below_date_percent_per_day.items() if str(i[0].strftime("%m"))==str(last_date.strftime("%m"))]
    dailyAboveGraph = {"x":[str(i[0].strftime("%H:%M")) for i in daily_above], "y":[i[1] for i in daily_above]}
    dailyBelowGraph = {"x":[str(i[0].strftime("%H:%M")) for i in daily_below], "y":[i[1] for i in daily_below]}
    weeklyAboveGraph = {"x":[str(i[0]) for i in weekly_above], "y":[str(i[1]) for i in weekly_above]}
    weeklyBelowGraph = {"x":[str(i[0]) for i in weekly_below], "y":[str(i[1]) for i in weekly_below]}
    monthlyAboveGraph = {"x":[str(i[0]) for i in monthly_above], "y":[str(i[1]) for i in monthly_above]}
    monthlyBelowGraph = {"x":[str(i[0]) for i in monthly_below], "y":[str(i[1]) for i in monthly_below]}
    dailyAboveEquip = [{"equip":equip[0], "temp":equip[2], "time":str(equip[-1])} for equip in level_1 if ((str(equip[-1].date())==str(last_date.date())) and (equip[2]>ABOVE_SET_POINT))]
    dailyBelowEquip = [{"equip":equip[0], "temp":equip[2], "time":str(equip[-1])} for equip in level_1 if ((str(equip[-1].date())==str(last_date.date())) and (equip[2]<=ABOVE_SET_POINT))]
    weeklyAboveEquip = [{"equip":equip[0], "temp":equip[2], "time":str(equip[-1])} for equip in level_1 if ((str(equip[-1].strftime("%V"))==str(last_date.strftime("%V"))) and (equip[2]>ABOVE_SET_POINT))]
    weeklyBelowEquip = [{"equip":equip[0], "temp":equip[2], "time":str(equip[-1])} for equip in level_1 if ((str(equip[-1].strftime("%V"))==str(last_date.strftime("%V"))) and (equip[2]<=ABOVE_SET_POINT))]
    monthlyAboveEquip = [{"equip":equip[0], "temp":equip[2], "time":str(equip[-1])} for equip in level_1 if ((str(equip[-1].strftime("%m"))==str(last_date.strftime("%m"))) and (equip[2]>ABOVE_SET_POINT))]
    monthlyBelowEquip = [{"equip":equip[0], "temp":equip[2], "time":str(equip[-1])} for equip in level_1 if ((str(equip[-1].strftime("%m"))==str(last_date.strftime("%m"))) and (equip[2]<=ABOVE_SET_POINT))]
    
    EQUIPPOINTS = {"daily":{"above":dailyAboveEquip, "below":dailyBelowEquip},
                    "weekly":{"above":weeklyAboveEquip, "below":weeklyBelowEquip},
                    "monthly":{"above":monthlyAboveEquip, "below":monthlyBelowEquip}}
    graphPoints = {"daily":{"above":dailyAboveGraph, "below":dailyBelowGraph},
                    "weekly":{"above":weeklyAboveGraph, "below":weeklyBelowGraph},
                    "monthly":{"above":monthlyAboveGraph, "below":monthlyBelowGraph}}
    
    THERMAL_DATA = [[e[0], e[1], round(float(e[3]), 1)] for e in all_thermal_equip]
    thermal_towers = {"tower1":{"equip":[], "levels":[]},"tower2":{"equip":[], "levels":[]}, "tower3":{"equip":[], "levels":[]}}
    for EQUIP in THERMAL_DATA:
        if EQUIP[1].split("-")[0][-1]=="3":
            thermal_towers["tower1"]["equip"].append(EQUIP[:2])
            thermal_towers["tower1"]["levels"].append(EQUIP[1].split("-")[1])
        elif EQUIP[1].split("-")[0][-1]=="4":
            thermal_towers["tower2"]["equip"].append(EQUIP[:2])
            thermal_towers["tower2"]["levels"].append(EQUIP[1].split("-")[1])
        elif EQUIP[1].split("-")[0][-1]=="5":
            thermal_towers["tower3"]["equip"].append(EQUIP[:2])
            thermal_towers["tower3"]["levels"].append(EQUIP[1].split("-")[1])
    thermal_towers["tower1"]["levels"] = sorted(list(set(thermal_towers["tower1"]["levels"])), reverse=False)
    thermal_towers["tower2"]["levels"] = sorted(list(set(thermal_towers["tower2"]["levels"])), reverse=False)
    thermal_towers["tower3"]["levels"] = sorted(list(set(thermal_towers["tower3"]["levels"])), reverse=False)
    return render(request=request, template_name="ThermalComfortCO2.html", context={"THERMAL":thermal_towers, "aboveAvg":above_avg, "belowAvg":below_avg, 
                                                    "aboveThresh":ABOVE_SET_POINT, "belowThresh":BELOW_SET_POINT, "aboveTempAvg":above_temp_avg, "belowTempAvg":below_temp_avg,
                                                    "graphPoints":graphPoints, "EQUIP":EQUIPPOINTS})
    

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
    def daysConvertor(d):
        if d>6:return d-7
        else: return d
    results = requests.get("http://api.openweathermap.org/data/2.5/forecast?id=2147714&units=metric&appid=c394c5e0aec171094aa6e1083e1e40e1").json()
    current_datetime = datetime.now()
    for cuurent_weather_data in results['list']:
        date_varialble = datetime.strptime(cuurent_weather_data["dt_txt"], "%Y-%m-%d %H:%M:%S")
        starting_weekday = date_varialble.weekday()
        starting_date = date_varialble.date()
        if abs((current_datetime - date_varialble).total_seconds())>18000: break
    
    data = {"0":{"temp":cuurent_weather_data["main"]["temp"], "feels_like":cuurent_weather_data["main"]["feels_like"], "pressure":cuurent_weather_data["main"]["pressure"]/1000,
        "humidity":cuurent_weather_data["main"]["humidity"], "status":cuurent_weather_data["weather"][0]["main"], "icon":cuurent_weather_data["weather"][0]["icon"], "wind_speed":cuurent_weather_data["wind"]["speed"],
        "wind_direction":cuurent_weather_data["wind"]["deg"], "vision":cuurent_weather_data["visibility"]/1000, "day":f"{starting_weekday}", "date":starting_date.day, "month":str(starting_date.strftime("%b")).upper()},
    "1":{"temp":results['list'][6]["main"]["temp"], "feels_like":results['list'][6]["main"]["feels_like"], "pressure":results['list'][6]["main"]["pressure"]/1000,
        "humidity":results['list'][6]["main"]["humidity"], "status":results['list'][6]["weather"][0]["main"], "icon":results['list'][6]["weather"][0]["icon"], "wind_speed":results['list'][6]["wind"]["speed"],
        "wind_direction":results['list'][6]["wind"]["deg"], "vision":results['list'][6]["visibility"]/1000, "day":f"{daysConvertor(starting_weekday+1)}", "date":str(starting_date.day)},
    "2":{"temp":results['list'][14]["main"]["temp"], "feels_like":results['list'][14]["main"]["feels_like"], "pressure":results['list'][14]["main"]["pressure"]/1000,
        "humidity":results['list'][14]["main"]["humidity"], "status":results['list'][14]["weather"][0]["main"], "icon":results['list'][14]["weather"][0]["icon"], "wind_speed":results['list'][14]["wind"]["speed"],
        "wind_direction":results['list'][14]["wind"]["deg"], "vision":results['list'][14]["visibility"]/1000,"day":f"{daysConvertor(starting_weekday+2)}"},
    "3":{"temp":results['list'][22]["main"]["temp"], "feels_like":results['list'][22]["main"]["feels_like"], "pressure":results['list'][22]["main"]["pressure"]/1000,
        "humidity":results['list'][22]["main"]["humidity"], "status":results['list'][22]["weather"][0]["main"], "icon":results['list'][22]["weather"][0]["icon"], "wind_speed":results['list'][22]["wind"]["speed"],
        "wind_direction":results['list'][22]["wind"]["deg"], "vision":results['list'][22]["visibility"]/1000, "day":f"{daysConvertor(starting_weekday+3)}"},
    "4":{"temp":results['list'][30]["main"]["temp"], "feels_like":results['list'][30]["main"]["feels_like"], "pressure":results['list'][30]["main"]["pressure"]/1000,
        "humidity":results['list'][30]["main"]["humidity"], "status":results['list'][30]["weather"][0]["main"], "icon":results['list'][30]["weather"][0]["icon"], "wind_speed":results['list'][30]["wind"]["speed"],
        "wind_direction":results['list'][30]["wind"]["deg"], "vision":results['list'][30]["visibility"]/1000,"day":f"{daysConvertor(starting_weekday+4)}"},
    "5":{"temp":results['list'][38]["main"]["temp"], "feels_like":results['list'][38]["main"]["feels_like"], "pressure":results['list'][38]["main"]["pressure"]/1000,
        "humidity":results['list'][38]["main"]["humidity"], "status":results['list'][38]["weather"][0]["main"], "icon":results['list'][38]["weather"][0]["icon"], "wind_speed":results['list'][38]["wind"]["speed"],
        "wind_direction":results['list'][38]["wind"]["deg"], "vision":results['list'][38]["visibility"]/1000,"day":f"{daysConvertor(starting_weekday+5)}"}}
    return render(request=request, template_name="weatherForcast.html", context={"weather":data})

def eotf(request):
    #if request.user.is_authenticated: return render(request=request, template_name="EOTF.html")
    #else: return redirect("home")
    return render(request=request, template_name="EOTF.html")

def eotf_cube(request):
    #if request.user.is_authenticated: return render(request=request, template_name="EOTF.html")
    #else: return redirect("home")
    return render(request=request, template_name="EOTF_cube.html")

def eotf_use(request):
    #if request.user.is_authenticated: return render(request=request, template_name="EOTF.html")
    #else: return redirect("home")
    return render(request=request, template_name="EOTF_use.html")

def traffic(request):
    #if request.user.is_authenticated: return render(request=request, template_name="EOTF.html")
    #else: return redirect("home")
    response = requests.get('https://api.transport.nsw.gov.au/v1/live/hazards/incident/open', 
                        headers={'Accept': 'application/json','Authorization': 'apikey g0792hSuYtu6sAOXdkrkYgowrSmymxVeCHsp',}).json()
    all_incidents = []
    for ind, incident in enumerate(response["features"]):
        incident_id = incident["id"]
        try: incident_weblink = incident["properties"]["webLinks"][0]["linkURL"]
        except: incident_weblink = ""
        incident_headlines = incident["properties"]["headline"]
        if incident["properties"]["expectedDelay"]==-1: incident_expected_delay = ""
        else: incident_expected_delay = str(datetime.fromtimestamp(int(str(incident["properties"]["expectedDelay"])[:10])).strftime('%H:%M:%S'))
        try:incident_started = str(datetime.fromtimestamp(int(str(incident["properties"]["created"])[:10])).strftime('%Y-%m-%d %H:%M:%S'))
        except: incident_started = ""
        try:incident_updated = str(datetime.fromtimestamp(int(str(incident["properties"]["lastUpdated"])[:10])).strftime('%Y-%m-%d %H:%M:%S'))
        except: incident_updated = ""
        if incident["properties"]["isMajor"]: incident_major = "Yes"
        else: incident_major = "No"
        incident_diversions = incident["properties"]["diversions"]
        try:incident_map = incident["properties"]["encodedPolylines"][0]["coords"]
        except: incident_map = ""
        try: incident_catagory = incident["properties"]["mainCategory"]
        except: incident_catagory = "---"
        try: incident_desciption = incident["properties"]["displayName"]
        except: incident_desciption = "---"
        incident_location = incident["properties"]["roads"]
        incident_location = incident_location[0]["crossStreet"] + "," + incident_location[0]["mainStreet"] + "," + incident_location[0]["region"] + ",Australia"
        if incident["properties"]["impactingNetwork"]: incident_impected = "Yes"
        else:incident_impected = "No"
        if incident["properties"]["isInitialReport"]: incident_initial  = "Yes"
        else: incident_initial = "No"
        all_incidents.append({"id":str(incident_id),"catagory":incident_catagory, "description":incident_desciption, "location":incident_location, "etd":incident_expected_delay,
                            "started":incident_started, "updated":incident_updated, "impact":incident_impected, "major":incident_major, "initial":incident_initial,
                            "headlines":incident_headlines, "diversion":incident_diversions, "weblinkI":incident_weblink, "google":incident_map, "coord":{"lng":incident["geometry"]["coordinates"][0], "lat": incident["geometry"]["coordinates"][1]}})
    return render(request=request, template_name="Traffic.html", context={"data":all_incidents})