from django.shortcuts import render
from django.http import HttpResponse
from django.db import connection
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.shortcuts import redirect
# from django.http import JsonResponse
import random
import string

# Create your views here.


def list(requests):
    features = 'employee'
    featuresname = '人員管理'
    pkind = "list"
    nodata = ''
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM employee order by ndate desc limit 0,20 ")
            # 获取列名
            columns = [col[0] for col in cursor.description]
            # 获取所有结果
            rows = cursor.fetchall()
            # 将结果转换为字典列表
            results = [dict(zip(columns, row)) for row in rows]
        if not results :
            nodata = '暫無資料'
    except ObjectDoesNotExist:
        return render(requests, "pages/employee/list.html", locals())
    except MultipleObjectsReturned:
        return render(requests, "pages/employee/list.html", locals())
    return render(requests, "pages/employee/list.html", locals())


def add(requests):
    features = 'employee'
    featuresname = '人員管理'
    id = ''
    nowdate = datetime.now().strftime('%Y-%m-%d')
    datas = [{
        'Eid': '',
        'NDate': datetime(2024, 8, 15),
        'IsOnline': 1,
        'IsLock': 0,
        'EmpNo': '',
        'Name': '',
        'Mobile': '',
        'Tel': '',
        'Account': '',
        'pwd': '',
        'IsAdmin': 0,
    }]
    return render(requests, "pages/employee/edit.html",locals())


def edit(requests, Eid):
    features = 'employee'
    featuresname = '人員管理'
    try:
        id = Eid

        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM employee where Eid=%s",Eid)
            # 获取列名
            columns = [col[0] for col in cursor.description]
            # 获取所有结果
            rows = cursor.fetchall()
            # 将结果转换为字典列表
            datas = [dict(zip(columns, row)) for row in rows]
        return render(requests, "pages/employee/edit.html",locals())
    except ObjectDoesNotExist:
        return redirect('./list')
    except MultipleObjectsReturned:
        return redirect('./list')
    return render(requests, "pages/employee/edit.html",locals())



def senddata(requests):
    features = 'meeting'
    featuresname = '會議管理'
    
    id = requests.POST.get('id')
    Ndate = requests.POST.get('Ndate')
    if Ndate=='':
        Ndate = datetime.now().strftime("%Y-%m-%d")
    Mobile = requests.POST.get('Mobile')
    EmpNo = requests.POST.get('EmpNo')
    IsLock = requests.POST.get('IsLock')
    IsOnline = requests.POST.get('IsOnline')
    Tel = requests.POST.get('Tel')
    Account = requests.POST.get('Account')
    pwd = requests.POST.get('pwd')
    IsAdmin = requests.POST.get('IsAdmin')
    
    
    
    if id!='':
        msg = '修改完成'
        with connection.cursor() as cursor:
            cursor.execute("update meeting_main set Mdate=%s ,Subject=%s,Subtitle=%s,Contents=%s,Langu=%s,Participants=%s,Master=%s WHERE MMid=%s",[Mdate,Subject,Subtitle,Contents,language,Participants,Master,id] )
    else:
        msg = '新增完成'
        characters = string.ascii_letters + string.digits
        # 生成指定长度的随机字符串
        secure = ''.join(random.choice(characters) for _ in range(80))
        Eid = requests.session.get('Eid','0')
        with connection.cursor() as cursor:
            cursor.execute("insert into meeting_main (Ndate,Mdate,Subject,Subtitle,Contents,Langu,Participants,Master,Secret,UDate,UpdateEid) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ",[Ndate,Mdate,Subject,Subtitle,Contents,language,Participants,Master,secure,datetime.now(),Eid] )
    return render(requests, "pages/meeting/edit.html",locals())
