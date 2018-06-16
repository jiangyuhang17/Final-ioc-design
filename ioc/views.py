# -*- coding: utf-8 -*-  
from django.shortcuts import render,redirect
from datetime import datetime

# Create your views here.
from django.http import HttpResponse
from django.contrib.auth.hashers import make_password, check_password
from ioc.models import AccountInfo,UserInfo,CarInfo,CarDriveRecord,Information,CarMinuteRecord,WarnInfomation
import json

import pandas
from sklearn.cluster import MeanShift
import numpy as np
import matplotlib.pyplot as plt
from math import radians, cos, sin, asin, sqrt
import random

#主界面模块
def ioc(request):
    #确认登录功能
    if request.method == "GET":
        member_id = request.session.get('member_id')
        if member_id == None:
            return redirect('signin')
        else:
            acc = AccountInfo.objects.get(id=member_id)
            fuser = UserInfo.objects.filter(accountinfo=acc)
            if len(fuser) == 0:
                user_info = UserInfo(uname='无名', usex=0, \
                                     ubirth_year=1970, \
                                     ubirth_month=1, \
                                     udrive_year=0, \
                                     uaddress='北京市', uphone=11111111111, \
                                     accountinfo=acc)
                user_info.save()
                acc.userinfo_status = 1
                acc.save()
                request.session['mywarn'] = 0
                return render(request, 'ioc/main.html',{"uname": acc.account, "mywarn": request.session["mywarn"]})
            user = fuser[0]
            car = CarInfo.objects.filter(userinfo=user)
            warninfo = WarnInfomation.objects.filter(userinfo=user,display=2)
            request.session['mywarn'] = len(warninfo)
            return render(request,'ioc/main.html',{"uname":acc.account,"car":car,"mywarn":request.session["mywarn"]})

#用户信息界面模块
def userinfo(request):
    acc = AccountInfo.objects.get(id=request.session['member_id'])
    user = UserInfo.objects.get(accountinfo=acc)
    car = CarInfo.objects.filter(userinfo=user)
    if request.method == 'GET':
        if acc.userinfo_status==1:

            return render(request,'ioc/main_userinfo.html',{"uname":acc.account,"car":car,"user":user,"mywarn":request.session["mywarn"]})
        else:
            return render(request,'ioc/main_userinfo_not.html',{"uname":acc.account,"car":car,"mywarn":request.session["mywarn"]})

#已经填写信息的用户编辑
def userinfo_edit(request):
    if request.method == 'GET':
        acc = AccountInfo.objects.get(id=request.session['member_id'])
        if acc.userinfo_status==1:
            user = UserInfo.objects.filter(accountinfo=acc)
            return render(request,'ioc/main_userinfo_edit.html',{"uname":acc.account,"user":user[0],"mywarn":request.session["mywarn"]})
        else:
            return render(request,'ioc/main_userinfo_input.html',{"uname":acc.account,"mywarn":request.session["mywarn"]})
    if request.method == 'POST':
        post = request.POST
        name = post['uname']
        sex = post['usex']
        birth_year = post['uyear']
        birth_month = post['umonth']
        drive_year = post['udrive_year']
        address = post['uaddress']
        phone = post['uphone']
        acc = AccountInfo.objects.get(id=request.session['member_id'])
        if acc.userinfo_status==1:
            user = UserInfo.objects.get(accountinfo=acc)
            user.uname=name
            user.usex=int(sex)
            user.ubirth_year=int(birth_year)
            user.ubirth_month=int(birth_month)
            user.udrive_year=int(drive_year)
            user.uaddress=address
            user.uphone=phone
            user.accountinfo
            user.save()
        else:
            user_info = UserInfo(uname=name, usex=int(sex), \
                                 ubirth_year=int(birth_year), \
                                 ubirth_month=int(birth_month), \
                                 udrive_year=int(drive_year), \
                                 uaddress=address, uphone=phone, \
                                 accountinfo=acc)
            user_info.save()
            acc.userinfo_status = 1
            acc.save()
        return redirect('../userinfo')

#修改密码模块
def password(request):
    acc = AccountInfo.objects.get(id=request.session['member_id'])
    user = UserInfo.objects.get(accountinfo=acc)
    car = CarInfo.objects.filter(userinfo=user)
    if request.method == "GET":
        return render(request,'ioc/main_password.html',{"uname":acc.account,"car":car,"mywarn":request.session["mywarn"]})
    if request.method == "POST":
        post = request.POST
        origin = post["originpa"]
        new = post["newpass"]
        renew= post["renewpass"]

        if check_password(origin,acc.password)!=True:
            return render(request, 'ioc/main_password.html', {"uname":acc.account,"car":car,"mywarn":request.session["mywarn"], "originerror": "originerror()"})
        elif origin == new:
            return render(request, 'ioc/main_password.html', {"uname":acc.account,"car":car,"mywarn":request.session["mywarn"], "sameerror": "sameerror()"})
        elif new != renew:
            return render(request,'ioc/main_password.html',{"uname":acc.account,"car":car,"mywarn":request.session["mywarn"],"repeaterror":"repeaterror()"})
        else:
            acc.password = make_password(new)
            acc.save()
            return render(request, 'ioc/main_password.html', {"uname":acc.account,"car":car, "change": "change()","mywarn":request.session["mywarn"]})

#mywarn模块
def userwarning(request):
    acc = AccountInfo.objects.get(id=request.session['member_id'])
    user = UserInfo.objects.get(accountinfo=acc)
    car = CarInfo.objects.filter(userinfo=user)
    warninfo = WarnInfomation.objects.filter(userinfo=user).order_by('-time')
    if request.method == "GET":
        return render(request,'ioc/main_userwarn.html',{"uname":acc.account,"car":car,"warninfo":warninfo,"mywarn":request.session["mywarn"]})


def warning_ajax(request):
    type = request.POST["type"]
    warn_id = request.POST["warning_id"]
    if type=="read":
        warninfo = WarnInfomation.objects.get(id=warn_id)
        warninfo.display = 1
        warninfo.save()
        if request.session['mywarn'] > 0:
            request.session['mywarn'] = request.session['mywarn']-1
        return HttpResponse('ok')
    if type=="ignore":
        warninfo = WarnInfomation.objects.get(id=warn_id)
        if warninfo.display == 2:
            if request.session['mywarn'] > 0:
                request.session['mywarn'] = request.session['mywarn'] - 1
        warninfo.display = 0
        warninfo.save()
        return HttpResponse('ok')

def warning_add(request):
    acc = AccountInfo.objects.get(id=request.session['member_id'])
    user = UserInfo.objects.get(accountinfo=acc)
    type = request.POST["type"]
    if type=="oil20":
        warninfo = WarnInfomation(display=2, color=1, content='油箱油量不足20L', time=datetime.now(), userinfo=user)
        warninfo.save()
        request.session["mywarn"] = request.session["mywarn"] + 1
        return HttpResponse('ok')
    if type=="oil10":
        warninfo = WarnInfomation(display=2, color=0, content='油箱油量不足10L', time=datetime.now(), userinfo=user)
        warninfo.save()
        request.session["mywarn"] = request.session["mywarn"] + 1
        return HttpResponse('ok')
    if type=="pressurelow":
        warninfo = WarnInfomation(display=2,color=0,content='汽车胎压过低',time=datetime.now(),userinfo=user)
        warninfo.save()
        request.session["mywarn"] = request.session["mywarn"] + 1
        return HttpResponse('ok')
    if type=="pressurehigh":
        warninfo = WarnInfomation(display=2,color=1,content='汽车胎压过高',time=datetime.now(),userinfo=user)
        warninfo.save()
        request.session["mywarn"] = request.session["mywarn"] + 1
        return HttpResponse('ok')
    if type=="templow":
        warninfo = WarnInfomation(display=2,color=0,content='汽车水温过低',time=datetime.now(),userinfo=user)
        warninfo.save()
        request.session["mywarn"] = request.session["mywarn"] + 1
        return HttpResponse('ok')
    if type=="temphigh":
        warninfo = WarnInfomation(display=2,color=1,content='汽车水温过高',time=datetime.now(),userinfo=user)
        warninfo.save()
        request.session["mywarn"] = request.session["mywarn"] + 1
        return HttpResponse('ok')

#汽车信息填写模块
def carinfo(request):
    acc = AccountInfo.objects.get(id=request.session['member_id'])
    user = UserInfo.objects.get(accountinfo=acc)
    car = CarInfo.objects.filter(userinfo=user)
    if request.method == "GET":
        return render(request,'ioc/main_carinfo.html',{"uname":acc.account,"car":car,"mywarn":request.session["mywarn"]})

    if request.method == "POST":
        post = request.POST
        cid = post["cid"]
        cbrand = post["cbrand"]
        cdisplace = post["cdisplace"]
        cbirth_year = post["cbirth_year"]
        cbirth_month = post["cbirth_month"]
        cuse_year = post["cuse_year"]
        cuse_month = post["cuse_month"]
        car = CarInfo(cid=cid,cbrand=cbrand,cdisplace=cdisplace,\
                      cbirth_year=cbirth_year,cbirth_month=cbirth_month,\
                      cuse_year=cuse_year,cuse_month=cuse_month,
                      userinfo=user)
        car.save()
        return redirect('/')

def carinfoedit(request,car_id):
    acc = AccountInfo.objects.get(id=request.session['member_id'])
    user = UserInfo.objects.get(accountinfo=acc)
    car = CarInfo.objects.get(id=car_id)
    if request.method == "GET":
        return render(request,'ioc/main_carinfo_edit.html',{"car":car,"mywarn":request.session["mywarn"]})

    if request.method == "POST":
        post = request.POST
        car.cid = post["cid"]
        car.cbrand = post["cbrand"]
        car.cdisplace = post["cdisplace"]
        car.cbirth_year = post["cbirth_year"]
        car.cbirth_month = post["cbirth_month"]
        car.cuse_year = post["cuse_year"]
        car.cuse_month = post["cuse_month"]

        car.save()
        return redirect('/')

#删除汽车
def cardelete(request,car_id):
    car = CarInfo.objects.get(id=car_id)
    cardrive = CarDriveRecord.objects.filter(carinfo=car)
    carminute = CarMinuteRecord.objects.filter(carinfo=car)
    cardrive.delete()
    carminute.delete()
    car.delete()
    return redirect('/')

#车速
# def carspeed(request):
#     acc = AccountInfo.objects.get(id=request.session['member_id'])
#     user = UserInfo.objects.get(accountinfo=acc)
#     if request.method == "GET":
#         car = CarInfo.objects.filter(userinfo=user)
#         return render(request,'ioc/main_carspeed.html',{"uname":acc.account,"car":car,"mywarn":request.session["mywarn"]})

#转速
def carrotation(request):
    acc = AccountInfo.objects.get(id=request.session['member_id'])

    if request.method == "GET":
        user = UserInfo.objects.get(accountinfo=acc)
        car = CarInfo.objects.filter(userinfo=user)
        if len(car)==0:
            return render(request, 'ioc/main.html', {"uname": acc.account,"warnnn":"warnn()", "mywarn": request.session["mywarn"]})
        return render(request,'ioc/main_carrotation.html',{"uname":acc.account,"car":car,"mywarn":request.session["mywarn"]})

#油量
def carfuelremain(request):
    acc = AccountInfo.objects.get(id=request.session['member_id'])
    user = UserInfo.objects.get(accountinfo=acc)
    if request.method == "GET":
        car = CarInfo.objects.filter(userinfo=user)
        if len(car)==0:
            return render(request, 'ioc/main.html', {"uname": acc.account,"warnnn":"warnn()", "mywarn": request.session["mywarn"]})
        return render(request, 'ioc/main_carfuelremain.html', {"uname": acc.account, "car": car,"mywarn":request.session["mywarn"]})

#胎压
def carpressure(request):
    acc = AccountInfo.objects.get(id=request.session['member_id'])
    user = UserInfo.objects.get(accountinfo=acc)
    if request.method == "GET":
        car = CarInfo.objects.filter(userinfo=user)
        if len(car)==0:
            return render(request, 'ioc/main.html', {"uname": acc.account,"warnnn":"warnn()", "mywarn": request.session["mywarn"]})
        return render(request, 'ioc/main_carpressure.html', {"uname": acc.account, "car": car,"mywarn":request.session["mywarn"]})

#水温
def carwatertemp(request):
    acc = AccountInfo.objects.get(id=request.session['member_id'])
    user = UserInfo.objects.get(accountinfo=acc)
    if request.method == "GET":
        car = CarInfo.objects.filter(userinfo=user)
        if len(car)==0:
            return render(request, 'ioc/main.html', {"uname": acc.account,"warnnn":"warnn()", "mywarn": request.session["mywarn"]})
        return render(request, 'ioc/main_carwatertemp.html', {"uname": acc.account, "car": car,"mywarn":request.session["mywarn"]})

#驾驶记录
def cardriveid(request,car_id):
    acc = AccountInfo.objects.get(id=request.session['member_id'])
    user = UserInfo.objects.get(accountinfo=acc)
    if request.method == "GET":
        car = CarInfo.objects.filter(userinfo=user)
        if len(car)==0:
            return render(request,'ioc/main_cardrive.html',{"uname":acc.account})
        if car_id==0:
            record = CarDriveRecord.objects.filter(carinfo=car[0]).order_by('-year', '-month', '-day')
            return render(request, 'ioc/main_cardrive.html',{"uname": acc.account,"mywarn":request.session["mywarn"], "car": car, "record": record, "fcar": car[0]})
        fcar = CarInfo.objects.get(id=car_id)
        record = CarDriveRecord.objects.filter(carinfo=fcar).order_by('-year','-month','-day')
        return render(request, 'ioc/main_cardrive.html', {"uname": acc.account,"car":car,"record":record,"fcar":fcar,"mywarn":request.session["mywarn"]})

def cardrivegraphid(request,car_id):
    acc = AccountInfo.objects.get(id=request.session['member_id'])
    user = UserInfo.objects.get(accountinfo=acc)
    if request.method == "GET":
        car = CarInfo.objects.filter(userinfo=user)
        if len(car)==0:
            return render(request, 'ioc/main_cardrivegraph.html',{"uname":acc.account})
        fcar = CarInfo.objects.get(id=car_id)
        record = CarDriveRecord.objects.filter(carinfo=fcar).order_by('year','month','day')
        return render(request, 'ioc/main_cardrivegraph.html', {"uname": acc.account,"car":car,"record":record,"fcar":fcar,"mywarn":request.session["mywarn"]})

#安全评分
def carevaluate(request,car_id):
    acc = AccountInfo.objects.get(id=request.session['member_id'])
    user = UserInfo.objects.get(accountinfo=acc)
    if request.method == "GET":
        car = CarInfo.objects.filter(userinfo=user)
        if len(car)==0:
            return render(request,'ioc/main_carevaluate.html',{"uname":acc.account})
        if car_id==0:
            fcar = car[0]
        else:
            fcar = CarInfo.objects.get(id=car_id)
        record = CarDriveRecord.objects.filter(carinfo=fcar).order_by('-year','-month','-day')
        l = len(record)
        if l==0:
            return render(request, 'ioc/main_carevaluate.html',{"uname": acc.account, "car": car, "evaluation": 100, "mywarn": request.session["mywarn"]})
        temp=0
        for item in record:
            temp += 40*(item.overspeed)/20 +20*(item.overcar)/20+20*(item.rapidac)/20+20*(item.rapidde)/20
        eva = 100-temp/l
        if eva<80 and eva>=50:
            warninfo = WarnInfomation(display=2,color=1,content=fcar.cid+' 安全评分低于80',time=datetime.now(),userinfo=user)
            warninfo.save()
            request.session["mywarn"] = request.session["mywarn"]+1
        return render(request,'ioc/main_carevaluate.html',{"uname":acc.account,"car":car,"evaluation":eva,"mywarn":request.session["mywarn"]})

#gps位置
def gpsposition(request,car_id):
    acc = AccountInfo.objects.get(id=request.session['member_id'])
    user = UserInfo.objects.get(accountinfo=acc)
    car = CarInfo.objects.filter(userinfo=user)
    if request.method == "GET" and (car_id==1):
        return render(request,'ioc/main_gpssite.html',{"uname":acc.account,"car":car,"car_id":car_id,"mywarn":request.session["mywarn"]})
    else:
        return render(request,'ioc/main_gpssite1.html',{"uname":acc.account,"car":car,"mywarn":request.session["mywarn"]})
    # if request.method == "POST":
    #     gpsinfo = Information.objects.filter(car_id=car_id)[:2]
    #     data = []
    #     for gps in gpsinfo:
    #         item = {}
    #         item['longitude'] = gps.longitude
    #         item['latitude'] = gps.latitude
    #         data.append(item)
    #     return HttpResponse(json.dumps(data))


#登录模块
def signin(request):
    if request.method == "GET":
        return render(request,'ioc/signin.html',{})

    if request.method == "POST":
        post = request.POST
        uaccount = post["uname"]
        upassword = post["upassword"]
        acc = AccountInfo.objects.filter(account=uaccount)
        if len(acc) == 0:
            return render(request, 'ioc/signin.html', {"showerror": "showerror()"})
        judge = check_password(upassword,acc[0].password)
        if not judge:
            return render(request,'ioc/signin.html',{"showerror":"showerror()"})
        request.session['member_id'] = acc[0].id
        request.session['mywarn'] = 0
        return redirect('/')

#注册模块
def signup(request):
    if request.method == "GET":
        return render(request,'ioc/signup.html',{})

    if request.method == "POST":
        uaccount = request.POST['uname']
        upassword = request.POST['upassword']
        record = AccountInfo.objects.filter(account=uaccount)
        if len(record)!=0:
            return render(request,'ioc/signup.html',{"func":"showerror()"})
        user = AccountInfo(account=uaccount,password=make_password(upassword),actype=1)
        user.save()
        request.session['member_id'] = user.id
        request.session['mywarn'] = 0
        return render(request,'ioc/signup_info.html',{"account":uaccount})


#注册账户检查模块
def signup_ajax(request):
    uaccount = request.POST['uname']
    if uaccount=="" or uaccount==None:
        data = 1
        return HttpResponse(data)
    record = AccountInfo.objects.filter(account=uaccount)
    if  len(record)!=0:
        data = 2
        return HttpResponse(data)
    data = 0
    return HttpResponse(data)

#注册用户填写信息模块
def signup_info(request):
    post = request.POST
    name = post['uname']
    sex = post['usex']
    birth_year = post['uyear']
    birth_month = post['umonth']
    drive_year = post['udrive_year']
    address = post['uaddress']
    phone = post['uphone']

    account = post['account']
    acc = AccountInfo.objects.get(account=account)

    user_info = UserInfo(uname=name, usex=int(sex), \
                         ubirth_year=int(birth_year), \
                         ubirth_month=int(birth_month), \
                         udrive_year=int(drive_year), \
                         uaddress=address, uphone=phone, \
                         accountinfo=acc)
    user_info.save()
    acc.userinfo_status = 1
    acc.save()
    return redirect('/')

#登出模块
def logout(request):
    try:
        del request.session["member_id"]
    except KeyError:
        pass
    return redirect('signin')


# def admin_signup(request):
#     return render(request,'ioc/admin_signup.html')
#
# def admin_signup_res(request):
#     post = request.POST
#     ad = AccountInfo(account=post['adname'],password=make_password(post['adpassword']),actype=0)
#     ad.save()
#     return render(request,'ioc/signin.html')

# 获得对应汽车的所有gps经纬度
def gpsdata(car_id):
    gpsinfo = Information.objects.filter(car_id=car_id)
    positions = []
    for item in gpsinfo:
        position = {}
        position["longitude"] = item.longitude 
        position["latitude"] = item.latitude
        positions.append(position)
    return positions

# 经纬度计算距离
def distance(lon1, lat1, lon2, lat2):
    p = 0.017453292519943295     #Pi/180
    a = 0.5 - cos((lat2 - lat1) * p)/2 + cos(lat1 * p) * cos(lat2 * p) * (1 - cos((lon2 - lon1) * p)) / 2
    return 12742 * asin(sqrt(a)) #2*R*asin...

# 获得核心对象
def getCore(car_id,r,MinPts):
    positions = []
    positions =  gpsdata(car_id)
    L = len(positions)

    core = []
    core_not = []

    for i in range(L):
        domain = 0
        for j in range(L):
            dist = distance(positions[i]["longitude"],positions[i]["latitude"],positions[j]["longitude"],positions[j]["latitude"])
            if dist <= r:
                domain = domain+1
        if domain >= MinPts:
            core.append(positions[i])
        else:
            core_not.append(positions[i])

    longitude_list = []
    latitude_list = []
    longitude_core = []
    latitude_core = []
    longitude_not_core = []
    latitude_not_core = []
    for item in positions:
        longitude_list.append(item["longitude"])
        latitude_list.append(item["latitude"])
    for item in core:
        longitude_core.append(item["longitude"])
        latitude_core.append(item["latitude"])
    for item in core_not:
        longitude_not_core.append(item["longitude"])
        latitude_not_core.append(item["latitude"])

    # 显示gps散点图
    # plt.scatter(longitude_list, latitude_list, c="r", alpha=0.5, label="car position")
    # plt.xlabel("longitude")
    # plt.ylabel("latitude")
    # plt.legend(loc=2)
    # plt.title("origin GPS scatter pic")
    # plt.show()

    # # 显示gps的核心对象
    # plt.scatter(longitude_not_core, latitude_not_core, c="r", alpha=0.5, label="car position")
    # plt.scatter(longitude_core, latitude_core, c="g", alpha=0.5, label="core objects")
    # plt.xlabel("longitude")
    # plt.ylabel("latitude")
    # plt.legend(loc=2)
    # plt.title("Core Objects     ϵ %.3f MinPts %d"%(r,MinPts))
    # plt.show()

    return positions,core



def getCluster(car_id,r,MinPts):
    k = 0
    Cluster = []

    D,core=getCore(car_id,r,MinPts)
    L = len(D)


    listlen = len(core)
    positions = D[:]

    while listlen!=0:
        old = positions[:]
        rand = random.randint(0,listlen-1)
        Q = []
        Q.append(core[rand])
        positions.remove(core[rand])

        while Q != []:
            q = Q.pop(0)
            
            domain = 0
            domain_position = []
            for i in range(L):
                dist = distance(D[i]["longitude"],D[i]["latitude"],q["longitude"],q["latitude"])
                if dist <= r:
                    domain = domain+1
                    domain_position.append(D[i])
            if domain >= MinPts:
                for item in domain_position:
                    if item in positions:
                        Q.append(item)
                        positions.remove(item)
        k = k+1
        c = []
        for item in old:
            if item not in positions:
                c.append(item)
                if item in core:
                    core.remove(item)
        Cluster.append(c)

        listlen = len(core)

    # positions_longitude = []
    # positions_latitude = []
    # for item in positions:
    #     positions_longitude.append(item["longitude"])
    #     positions_latitude.append(item["latitude"])

    # plt.scatter(positions_longitude, positions_latitude, c="r", alpha=0.5, label="noisy")

    # ClusterOrder = []
    # clusterlen = len(Cluster)
    # if clusterlen > 3:
    #     for i in range(3):
    #         maxi = 0
    #         max_item = []
    #         for item in Cluster:
    #             if(len(item)>maxi):
    #                 maxi = len(item)
    #                 max_item = item
    #         ClusterOrder.append(max_item)
    #         Cluster.remove(max_item)
    #     clusterlen = 3
    #     Cluster = ClusterOrder

    # color = ["green","yellow","blue","black","orange","pink","gray"]
    # for i in range(clusterlen):
    #     positions_longitude = []
    #     positions_latitude = []
    #     for item in Cluster[i]:
    #         positions_longitude.append(item["longitude"])
    #         positions_latitude.append(item["latitude"])
    #     plt.scatter(positions_longitude, positions_latitude, c=color[i], alpha=0.5, label="car")

    # plt.xlabel("longitude")
    # plt.ylabel("latitude")
    # plt.legend(loc=2)
    # plt.title("active position     ϵ %.3f MinPts %d"%(r,MinPts))
    # plt.show()
    return Cluster

#活跃地区
def regular(request,car_id):
    acc = AccountInfo.objects.get(id=request.session['member_id'])
    user = UserInfo.objects.get(accountinfo=acc)
    car = CarInfo.objects.filter(userinfo=user)
    if request.method=="GET":
        return render(request, 'ioc/main_regular.html', {"uname":acc.account,"car":car,"car_id":car_id,"mywarn":request.session["mywarn"]})
    if request.method=="POST":
        Clusters = getCluster(car_id+1,0.5,10)
        list = []
        for item in Clusters:
            for itemm in  item:
                list.append(itemm)
        data = list
        # df = pandas.DataFrame(columns = ['longitude','latitude'])
        # for location in locations:
        #     df = df.append({'longitude':location.longitude,'latitude':location.latitude}, ignore_index=True)
        # input = np.array(df)
        # clf = MeanShift()
        # clf.fit(input)
        # centroids = clf.cluster_centers_
        # list = []
        # if len(centroids) >= 3:
        #     for i in range(0, 3):
        #         item = {}
        #         item['longitude'] = centroids[i][0]
        #         item['latitude'] = centroids[i][1]
        #         list.append(item)
        # else:
        #     for i in range(0, len(centroids)):
        #         item = {}
        #         item['longitude'] = centroids[i][0]
        #         item['latitude'] = centroids[i][1]
        #         list.append(item)
        # data = list
        return HttpResponse(json.dumps(data))



