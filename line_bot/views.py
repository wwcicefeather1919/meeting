from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
# 引入資料庫連接
from django.db import connection
# 引入時間套件
from datetime import datetime
# 加密套件
import hashlib
# 引入 linebot SDK
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextSendMessage, TextMessage, StickerMessage, ImageMessage


# 建立 linebot classs 進行連線
line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)


@csrf_exempt
def callback(request):
    if (request.method == "POST"):
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')

        # 嘗試解密event
        try:
            events = parser.parse(body, signature)
        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()

        for event in events:
            if isinstance(event, MessageEvent):
                uid = event.source.user_id
                res_text = str(event.message.text)
                print(uid)
                print(res_text)
                with connection.cursor() as cursor:
                    # 查詢資料
                    cursor.execute("SELECT name FROM employee WHERE LineID = %s", uid)
                    rows = cursor.fetchall()
                    # 檢查是否有資料
                    if rows:
                        # 有資料，判斷姓名等欄位是否有資料
                        if res_text[0:2]=="@@":
                            ary = res_text.split("@@")
                            cursor.execute("update employee set name=%s ,Account=%s,Password=%s WHERE LineID=%s",[ary[1],ary[2],hashlib.md5(ary[3].encode('utf-8')).hexdigest(), uid] )
                            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="設定完成"))
                        elif  res_text!="":
                            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="資料格式錯誤"))
                        else:
                            for row in rows:
                                if row[0]=='' or row[0] is None :
                                    line_bot_api.reply_message(event.reply_token, TextSendMessage(text="1請輸入@@姓名@@帳號@@密碼，例如@@陳水扁@@chen@@1234"))
                    else:
                        now = datetime.now()
                        cursor.execute("insert into employee (NDate,UDate,LineID) values( %s , %s , %s )",[now , now, uid] )
                        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="2請輸入@@姓名@@帳號@@密碼，例如@@陳水扁@@chen@@1234"))
                        
                
                
                
                
                
                # if isinstance(event.message, TextMessage):
                #     res_text = event.message.text
                #     print(res_text)
                #     if res_text == '@我要報到':
                #         line_bot_api.reply_message(event.reply_token, StickerMessage(package_id=446, sticker_id=1988))
                #     elif res_text == '@我的名牌':
                #         line_bot_api.reply_message(event.reply_token, TextSendMessage(text="456"))
                #     elif res_text == '@車號登入':
                #         line_bot_api.reply_message(event.reply_token, TextSendMessage(text="456"))
                #     else:
                #         line_bot_api.reply_message(event.reply_token, TextSendMessage(text=res_text))
                        
                

        return HttpResponse()
    else:
        return HttpResponseBadRequest()


def sendMsg(requests, uid, msg):
    # push_message 因為會有收費問題，所以可以建議改用 reply_message
    line_bot_api.push_message(uid, TextSendMessage(text=msg))
    return HttpResponse()

# 傳送各聊天室的使用者連結網址
def sendTokenLink(requests, uid, msg):
    # push_message 因為會有收費問題，所以可以建議改用 reply_message
    line_bot_api.push_message(uid, TextSendMessage(text=msg))
    return HttpResponse()
