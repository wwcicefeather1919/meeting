from django.shortcuts import render
from django.http import HttpResponse
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.shortcuts import redirect
from django.http import JsonResponse
import json
# 
import hashlib
# 引入資料庫連接
from django.db import connection
# 引入 linebot SDK
from django.conf import settings
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import  TextSendMessage
# 抓取 templates 的 static
from django.templatetags.static import static
from translator.views import translator_text


def invite(requests,Secret,Eid):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM meeting_main where Secret=%s",Secret)
            # 获取列名
            columns = [col[0] for col in cursor.description]
            # 获取所有结果
            rows = cursor.fetchall()
            # 将结果转换为字典列表
            results = [dict(zip(columns, row)) for row in rows]
        Participants = []
        for item in results:
            MMid = item["MMid"]
            # 當人員為主持人，抓取與會人員
            if f',{Eid},' in item["Master"]:
                if item["Participants"] !="":
                    with connection.cursor() as cursor2:
                        # 取得與會人員相關資料
                        Participant = item["Participants"][1:-1]
                        print(Participant)
                        cursor2.execute(f"SELECT Eid,Name,Title,LineID FROM employee where Eid in ({Participant})")
                        # 获取列名
                        columns2 = [col2[0] for col2 in cursor2.description]
                        # 获取所有结果
                        rows2 = cursor2.fetchall()
                        
                        Participants = [dict(zip(columns2, row2)) for row2 in rows2]
                        

                    #取得請求人員
                    ask = []
                    with connection.cursor() as cursor2:
                        # 取得與會人員相關資料
                        cursor2.execute("SELECT a.*,b.Name,b.Title FROM meeting_chatroom_emp as a left join employee as b on a.Eid=b.Eid where a.MMid=%s and a.isallow=0",MMid)
                        # 获取列名
                        columns2 = [col[0] for col in cursor2.description]
                        # 获取所有结果
                        rows2 = cursor2.fetchall()
                        ask = [dict(zip(columns2, row2)) for row2 in rows2]
                    
                return render(requests, "pages/chatroom/invite.html", locals())
            else:
                return HttpResponse('非會議主持人員')
    except ObjectDoesNotExist:
        return HttpResponse('資料錯誤')
    except MultipleObjectsReturned:
        return HttpResponse('資料錯誤')
    return HttpResponse('資料錯誤')

# 發送邀約連結
def sendinvite(requests,Secret,Eids):
    linkurl = 'https://9104-2001-b400-e4f0-a09f-1cb2-3cb3-f0e9-d7bc.ngrok-free.app'
    try:
        with connection.cursor() as cursor:
            # 判斷驗證碼是否正確
            cursor.execute("SELECT MMid,Subject FROM meeting_main where Secret=%s",Secret)
            # 获取列名
            columns = [col[0] for col in cursor.description]
            # 获取所有结果
            rows = cursor.fetchall()
            # 将结果转换为字典列表
            results = [dict(zip(columns, row)) for row in rows]
            Participants = []
            for item in results:
                with connection.cursor() as cursor2:
                    # 取得勾選人員相關資料
                    cursor2.execute("SELECT * FROM employee where Eid in (%s)",Eids)
                    # 获取列名
                    columns2 = [col[0] for col in cursor2.description]
                    # 获取所有结果
                    rows2 = cursor2.fetchall()
                    results2 = [dict(zip(columns2, row2)) for row2 in rows2]
                    
                    # 建立 linebot classs 進行連線
                    line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
                    for item2 in results2:
                        msg = f"{ item2['Name'] }您好，\r\n您接受到一個會議邀請，\r\n會議主題：{item['Subject']}，\r\n請點擊聯結，前往會議室。\r\n"
                        msg += f"連結網址：{linkurl}/chatroom/check/{Secret}/{item2['Eid']}"
                        line_bot_api.push_message(item2['LineID'], TextSendMessage(text=msg))
                        
                return HttpResponse('ok')

    except ObjectDoesNotExist:
        return HttpResponse('資料錯誤')
    except MultipleObjectsReturned:
        return HttpResponse('資料錯誤')
    return HttpResponse('資料錯誤')


def check(requests,Secret,Eid):
    try:
        with connection.cursor() as cursor:
            # 判斷驗證碼是否正確
            cursor.execute(f"SELECT MMid FROM meeting_main where Secret=%s and Participants like %s",[Secret,f'%,{Eid},%'])
            rows = cursor.fetchall()
            if rows:
                for row in rows:
                    with connection.cursor() as cursor2:
                        # 判斷是否已新增到 meeting_chatroom_emp
                        cursor2.execute("SELECT MCEid,Isallow FROM meeting_chatroom_emp where MMid=%s and Eid=%s",[row[0],Eid])
                        rows2 = cursor2.fetchall()
                        if rows2:
                            # 有資料，判斷是否允許，若不允許，則在新增一筆，若已允許，跳往會議室
                            for row2 in rows2:
                                if row2[1]==1 :
                                    return redirect(f'/chatroom/room/{Secret}/{Eid}')
                                elif  row2[1]==2 :
                                    cursor2.execute("insert into meeting_chatroom_emp (NDate,MMid,Eid) values (%s,%s,%s)",[datetime.now(),row[0],Eid])
                                    # return HttpResponse('等待主持人員允許！')
                                    msg = '等待主持人員允許！'
                                    return render(requests, "pages/chatroom/wait.html", locals())
                                else:
                                    msg = '等待主持人員允許！'
                                    return render(requests, "pages/chatroom/wait.html", locals())
                        else:
                            # 沒資料，新增一筆
                            cursor2.execute("insert into meeting_chatroom_emp (NDate,MMid,Eid) values (%s,%s,%s)",[datetime.now(),row[0],Eid])
                            # return HttpResponse('等待主持人員允許！')
                            msg = '等待主持人員允許！'
                            return render(requests, "pages/chatroom/wait.html", locals())
            else:
                # return HttpResponse('會議室聯結錯誤或非會議相關人員')
                msg = '會議室聯結錯誤或非會議相關人員！'
                return render(requests, "pages/chatroom/wait.html", locals())
    except ObjectDoesNotExist:
        # return HttpResponse('會議室聯結錯誤')
        msg = '會議室聯結錯誤！'
        return render(requests, "pages/chatroom/wait.html", locals())
    except MultipleObjectsReturned:
        # return HttpResponse('會議室聯結錯誤')
        msg = '會議室聯結錯誤！'
        return render(requests, "pages/chatroom/wait.html", locals())
    #return HttpResponse('會議室聯結錯誤')
    msg = '會議室聯結錯誤！'
    return render(requests, "pages/chatroom/wait.html", locals())


def checkinvite(requests,MCEid,act):
    try:
        with connection.cursor() as cursor:
            # 判斷驗證碼是否正確
            cursor.execute(f"update meeting_chatroom_emp set Isallow=%s  where MCEid=%s",[act,MCEid])
            return HttpResponse('OK')
    except ObjectDoesNotExist:
        return HttpResponse('資料錯誤')
    except MultipleObjectsReturned:
        return HttpResponse('資料錯誤')
    return HttpResponse('資料錯誤')

def checkall(requests,Secret,act):
    try:
        with connection.cursor() as cursor:
            # 判斷驗證碼是否正確
            cursor.execute(f"SELECT MMid FROM meeting_main where Secret=%s",Secret)
            rows = cursor.fetchall()
            if rows:
                for row in rows:
                    with connection.cursor() as cursor2:
                        # 判斷是否已新增到 meeting_chatroom_emp
                        cursor.execute(f"update meeting_chatroom_emp set Isallow=%s where MMid=%s and Isallow=0 ",[act,row[0]])
                        
            else:
                return HttpResponse('資料錯誤')
    except ObjectDoesNotExist:
        return HttpResponse('資料錯誤')
    except MultipleObjectsReturned:
        return HttpResponse('資料錯誤')
    return HttpResponse('資料錯誤')




def room(requests,Secret,Eid,Langu='tw'):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT MMid,Subject FROM meeting_main where Secret=%s",Secret)
            rows = cursor.fetchall()
            for item in rows:
                members = []
                chatarray = []
                MMid = item[0]
                Subject = item[1]
                with connection.cursor() as cursor2:
                    # 取得與會人員相關資料
                    cursor2.execute("SELECT a.*,b.Name,b.Title FROM meeting_chatroom_emp as a left join employee as b on a.Eid=b.Eid where a.MMid=%s and a.isallow=1",item[0])
                    columns2 = [col[0] for col in cursor2.description]
                    rows2 = cursor2.fetchall()
                    members = [dict(zip(columns2, row2)) for row2 in rows2]
                    
                    # 取得聊天室內容
                    cursor2.execute("SELECT a.MCMid,a.MMid,a.Eid,a.message,b.Contents,b.readers,c.name,b.MCVid FROM meeting_chatroom_main as a left join meeting_chatroom_version as b on a.MCMid=b.MCMid left join employee as c on a.Eid=c.Eid where a.MMid=%s and b.Lange=%s order by a.NDate asc",[item[0],Langu])
                    columns2 = [col[0] for col in cursor2.description]
                    rows2 = cursor2.fetchall()
                    chatarray = [dict(zip(columns2, row2)) for row2 in rows2]
                    for item in chatarray:
                        item['type'] ="sent" if str(item['Eid'])==str(Eid) else "received"
                        if not f',{Eid},' in item["readers"]:
                            if item["readers"]=='':
                                cursor.execute("update meeting_chatroom_version set readers=%s where MCVid=%s",[f',{Eid},',item["MCVid"]])
                            else:
                                cursor.execute("update meeting_chatroom_version set readers=CONCAT(readers,%s) where MCVid=%s",[f',{Eid},',item["MCVid"]])
            return render(requests, "pages/chatroom/chatroom.html", locals())
    except ObjectDoesNotExist:
        return HttpResponse('資料錯誤')
    except MultipleObjectsReturned:
        return HttpResponse('資料錯誤')
    return render(requests, "pages/chatroom/chatroom.html", locals())


def send_messages(requests):
    if requests.method == 'POST':
        message = requests.POST.get('message')
        MMid = requests.POST.get('MMid')
        Eid = requests.POST.get('Eid')
        Langu = requests.POST.get('Langu')
    else:
        message = requests.GET.get('message')
        MMid = requests.GET.get('MMid')
        Eid = requests.GET.get('Eid')
        Langu = requests.GET.get('Langu')
    
    now = datetime.now()
    if message=='' or MMid=='' or Eid=='' :
        return HttpResponse('N,留言失敗')
    else:
        # 新增留言資料到 meeting_chatroom_main 
        with connection.cursor() as cursor:
            cursor.execute("insert into meeting_chatroom_main(NDate,MMid,Eid,message) values (%s,%s,%s,%s)",[now,MMid,Eid,message])
            MCMid = cursor.lastrowid
            #新增翻譯後的資料
            result = translator_text(MMid,MCMid,message)
            # cursor.execute("insert into meeting_chatroom_version(MMid,MCMid,Lange,Contents) values (%s,%s,%s,%s)",[MMid,MCMid,Langu,message])
            return HttpResponse(result)
        connection.commit()
    return HttpResponse('')

        
def load_messages(requests):
    
    if requests.method == 'POST':
        MMid = requests.POST.get('MMid')
        Eid = requests.POST.get('Eid')
        Langu = requests.POST.get('Langu')
    else:
        MMid = requests.GET.get('MMid')
        Eid = requests.GET.get('Eid')
        Langu = requests.GET.get('Langu')
        
    # 取得未讀留言
    with connection.cursor() as cursor:
        cursor.execute("SELECT a.MCMid,a.MMid,a.Eid,a.message,b.Contents,b.readers,c.name,b.MCVid FROM meeting_chatroom_main as a left join meeting_chatroom_version as b on a.MCMid=b.MCMid left join employee as c on a.Eid=c.Eid where a.MMid=%s and b.Lange=%s and readers not like %s",[MMid,Langu,f',{Eid},'])
        rows = cursor.fetchall()
        returnstr = ''
        if rows:
            for row in rows:
                
                returnstr += f'<div class="message { "sent" if str(row[2])==str(Eid) else "received" }">'
                returnstr += f'	<div class="info">'
                returnstr += f'		<img src="{static("img/11.jpg")}" alt="{row[6]}">'
                returnstr += f'		<div>'
                returnstr += f'			<div class="sender-name">{row[6]}</div>'
                returnstr += f'			<div class="bubble">{row[4]}</div>'
                returnstr += f'		</div>'
                returnstr += f'	</div>'
                returnstr += f'</div>'
                
                if row[5]=='':
                    cursor.execute("update meeting_chatroom_version set readers=%s where MCVid=%s",[f',{Eid},',row[7]])
                else:
                    cursor.execute("update meeting_chatroom_version set readers=CONCAT(readers,%s) where MCVid=%s",[f'{Eid},',row[7]])
                
            return HttpResponse(returnstr)
                    
        else:
            return HttpResponse('')
        
    connection.commit()
            
def load_member(requests,MMid):
    with connection.cursor() as cursor:
        # 取得與會人員相關資料
        cursor.execute("SELECT b.Name,b.Title FROM meeting_chatroom_emp as a left join employee as b on a.Eid=b.Eid where a.MMid=%s and a.isallow=1",MMid)
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
        members = [dict(zip(columns, row)) for row in rows]
        # print(members)
        return HttpResponse(json.dumps(members, ensure_ascii=False, indent=4))
    return HttpResponse('')
    