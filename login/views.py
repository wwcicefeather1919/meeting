from django.shortcuts import render
from django.http import HttpResponse
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.shortcuts import redirect
# from django.http import JsonResponse
import hashlib
# 引入資料庫連接
from django.db import connection

# Create your views here.


def login(requests):
    if requests.session.get('islogin', False) is True:
        return redirect('/index')
    return render(requests, "pages/login.html")


def index(requests):
    if requests.session.get('islogin', False) is False:
        return redirect('/login')
    return render(requests, "pages/index.html")


def logout(requests):
    requests.session['islogin'] = False
    requests.session['name'] = None
    requests.session['isadmin'] = None
    requests.session['Eid'] = None
    return redirect('/login')


def sendmsg(requests):
    account = requests.POST.get('account')
    pwd = requests.POST.get('password')
    pwd = hashlib.md5(pwd.encode('utf-8')).hexdigest()
    try:
        with connection.cursor() as cursor:
            # 查詢資料
            cursor.execute("SELECT name,isadmin,Eid FROM employee WHERE Account=%s and Password=%s limit 1 ", [account,pwd])
            rows = cursor.fetchall()
            # 檢查是否有資料
            if rows:
                for row in rows:
                    requests.session['islogin'] = True
                    requests.session['name'] = row[0]
                    requests.session['isadmin'] = row[1]
                    requests.session['Eid'] = row[2]
                return redirect('/index')
            else:
                errmsg = '帳號或密碼錯誤'
                return render(requests, "pages/login.html" ,locals())
    except ObjectDoesNotExist:
        return redirect('/login')
    except MultipleObjectsReturned:
        return redirect('/login')

    
