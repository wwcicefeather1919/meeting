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
    features = 'meeting'
    featuresname = '會議管理'
    pkind = "list"
    nodata = ''
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM meeting_main order by ndate desc limit 0,20 ")
            # 获取列名
            columns = [col[0] for col in cursor.description]
            # 获取所有结果
            rows = cursor.fetchall()
            # 将结果转换为字典列表
            results = [dict(zip(columns, row)) for row in rows]
            # print(results)
            
            for item in results:
                if item["Master"] !="":
                    Master = ''
                    with connection.cursor() as cursor2:
                        m = item["Master"][1:-1]
                        cursor2.execute(f"SELECT name FROM employee where Eid in ({m})",)
                        # 获取列名
                        columns2 = [col[0] for col in cursor2.description]
                        # 获取所有结果
                        rows2 = cursor2.fetchall()
                        results2 = [dict(zip(columns2, row2)) for row2 in rows2]
                        for item2 in results2:
                            Master += f'{item2["name"]},'
                        item["Master"] = Master
                
                if item["Participants"] !="":
                    Participants = ''
                    with connection.cursor() as cursor2:
                        p = item["Participants"][1:-1]
                        cursor2.execute(f"SELECT name FROM employee where Eid in ({p})",)
                        # 获取列名
                        columns2 = [col[0] for col in cursor2.description]
                        # 获取所有结果
                        rows2 = cursor2.fetchall()
                        results2 = [dict(zip(columns2, row2)) for row2 in rows2]
                        for item2 in results2:
                            Participants += f'{item2["name"]},'
                        item["Participants"] = Participants
            
            
            
            
        if not results :
            nodata = '暫無資料'
    except ObjectDoesNotExist:
        return render(requests, "pages/meeting/list.html", locals())
    except MultipleObjectsReturned:
        return render(requests, "pages/meeting/list.html", locals())
    return render(requests, "pages/meeting/list.html", locals())


def add(requests):
    features = 'meeting'
    featuresname = '會議管理'
    id = ''
    nowdate = datetime.now().strftime('%Y-%m-%d')
    datas = [{
        'MMid': '',
        'NDate': datetime(2024, 8, 15),
        'Secret': '',
        'Mdate': datetime(2024, 8, 19),
        'Subject': '',
        'Subtitle': '',
        'Contents': '',
        'Summary': '',
        'Langu': ',tw,en,',
        'Master': '',
        'Participants': '',
        'UDate': '',
        'UpdateEid': 1
    }]
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM employee order by eid desc limit 0,20 ")
            # 获取列名
            columns = [col[0] for col in cursor.description]
            # 获取所有结果
            rows = cursor.fetchall()
            # 将结果转换为字典列表
            employees = [dict(zip(columns, row)) for row in rows]
    except ObjectDoesNotExist:
        employees = []
    except MultipleObjectsReturned:
        employees = []
    print(nowdate)
    return render(requests, "pages/meeting/edit.html",locals())


def edit(requests, MMid):
    features = 'meeting'
    featuresname = '會議管理'
    Eid = requests.session.get('Eid','0') 
    datas = []
    employees = []
    try:
        id = MMid
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM employee order by eid desc limit 0,20 ")
            # 获取列名
            columns = [col[0] for col in cursor.description]
            # 获取所有结果
            rows = cursor.fetchall()
            # 将结果转换为字典列表
            employees = [dict(zip(columns, row)) for row in rows]
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM meeting_main where MMid=%s",MMid)
            # 获取列名
            columns = [col[0] for col in cursor.description]
            # 获取所有结果
            rows = cursor.fetchall()
            # 将结果转换为字典列表
            datas = [dict(zip(columns, row)) for row in rows]
        return render(requests, "pages/meeting/edit.html",locals())
    except ObjectDoesNotExist:
        return redirect('./list')
    except MultipleObjectsReturned:
        return redirect('./list')
    return render(requests, "pages/meeting/edit.html",locals())


def senddata(requests):
    features = 'meeting'
    featuresname = '會議管理'
    
    id = requests.POST.get('id')
    Ndate = requests.POST.get('Ndate')
    if Ndate=='':
        Ndate = datetime.now().strftime("%Y-%m-%d")
    Mdate = requests.POST.get('Mdate')
    Subject = requests.POST.get('Subject')
    Subtitle = requests.POST.get('Subtitle')
    Contents = requests.POST.get('Contents')
    
    language = ''
    for i in requests.POST.getlist('language[]'):
        language += f',{i},' if language=='' else f'{i},'
        
    Master = ''
    for i in requests.POST.getlist('Master[]'):
        Master += f',{i},' if Master=='' else f'{i},'
        
    Participants = ''
    for i in requests.POST.getlist('Participants[]'):
        Participants += f',{i},' if Participants=='' else f'{i},'
    print(Participants)
    
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


def checkrecord(requests,MMid,Langu='tw'):
    features = 'meeting'
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT MMid,Subject FROM meeting_main where MMid=%s",MMid)
            rows = cursor.fetchall()
            for item in rows:
                members = []
                chatarray = []
                MMid = item[0]
                Subject = item[1]
                with connection.cursor() as cursor2:
                    # 取得聊天室內容
                    cursor2.execute("SELECT a.MCMid,a.NDate,a.MMid,a.Eid,a.message,b.MCVid,b.Contents,c.name FROM meeting_chatroom_main as a left join meeting_chatroom_version as b on a.MCMid=b.MCMid left join employee as c on a.Eid=c.Eid where a.MMid=%s and b.Lange=%s order by a.NDate asc",[item[0],Langu])
                    columns2 = [col[0] for col in cursor2.description]
                    rows2 = cursor2.fetchall()
                    chatarray = [dict(zip(columns2, row2)) for row2 in rows2]
                    
            return render(requests, "pages/meeting/checkRecord.html", locals())
    except ObjectDoesNotExist:
        return HttpResponse('資料錯誤')
    except MultipleObjectsReturned:
        return HttpResponse('資料錯誤')
    return render(requests, "pages/meeting/checkRecord.html", locals())

def updaterecord(requests):
    features = 'meeting'
    if requests.method == 'POST':
        message = requests.POST.get('message')
        MCVid = requests.POST.get('MCVid')
    else:
        message = requests.GET.get('message')
        MCVid = requests.GET.get('MCVid')
    now = datetime.now()
    Eid = requests.session.get('Eid','0')
    if message=='' or MCVid=='' :
        return HttpResponse('N,修改失敗')
    else:
        # 新增留言資料到 meeting_chatroom_main 
        with connection.cursor() as cursor:
            cursor.execute("update meeting_chatroom_version set Contents=%s,UDate=%s,UpdateEid=%s where MCVid=%s",[message,now,Eid,MCVid])
            
            return HttpResponse('ok')
        connection.commit()
    return HttpResponse('')

def outputrecord(requests,MMid,Langu='tw'):
    features = 'meeting'
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT MMid,Subject FROM meeting_main where MMid=%s",MMid)
            rows = cursor.fetchall()
            for item in rows:
                chatarray = []
                MMid = item[0]
                Subject = item[1]
                with connection.cursor() as cursor2:
                    # 取得聊天室內容
                    cursor2.execute("SELECT a.MCMid,b.Contents,c.name FROM meeting_chatroom_main as a left join meeting_chatroom_version as b on a.MCMid=b.MCMid left join employee as c on a.Eid=c.Eid where a.MMid=%s and b.Lange=%s order by a.NDate asc",[item[0],Langu])
                    columns2 = [col[0] for col in cursor2.description]
                    rows2 = cursor2.fetchall()
                    chatarray = [dict(zip(columns2, row2)) for row2 in rows2]
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"record_{timestamp}.txt"
                    contentary = []
                    for item in chatarray:
                        contentary.append(f"{item['name']} : {item['Contents']} \r\n")
                        
                    result = "".join(contentary)  # 使用逗號和空格作為分隔符進行串接 
                    
                    response = HttpResponse(result, content_type='text/plain')
                    response['Content-Disposition'] = f'attachment; filename="{filename}"'
                    return response
            return render(requests, "pages/meeting/checkRecord.html", locals())
    except ObjectDoesNotExist:
        return HttpResponse('資料錯誤')
    except MultipleObjectsReturned:
        return HttpResponse('資料錯誤')
    return HttpResponse('')
   