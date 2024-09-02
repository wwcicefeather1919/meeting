"""
URL configuration for meeting project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from line_bot.views import callback, sendMsg
from login.views import login, index, sendmsg, logout
from meet.views import list, add as add_meet, edit as edit_meet, senddata as senddata_meet,checkrecord,updaterecord,outputrecord
from employee.views import list as list_emp, add as add_emp, edit as edit_emp, senddata as senddata_emp
from chatroom.views import invite, room, sendinvite, check, checkinvite, checkall, send_messages, load_messages, load_member
from translator.views import process_audio, translator_text


urlpatterns = [
    path('', login),
    path('login/', login),
    path('index', index),
    path('senddata', sendmsg),
    path('logout/', logout), 
    
    path('meeting/list', list),
    path('meeting/add', add_meet),
    path('meeting/edit/<str:MMid>', edit_meet),
    path('meeting/senddata', senddata_meet),
    path('meeting/checkrecord/<str:MMid>', checkrecord),
    path('meeting/checkrecord/<str:MMid>/<str:Langu>', checkrecord),
    path('meeting/updaterecord', updaterecord),
    path('meeting/outputrecord/<str:MMid>/<str:Langu>', outputrecord),
    
    
    path('chatroom/invite/<str:Secret>/<str:Eid>', invite),
    path('chatroom/sendinvite/<str:Secret>/<str:Eids>', sendinvite),
    path('chatroom/check/<str:Secret>/<str:Eid>', check),
    path('chatroom/checkinvite/<str:MCEid>/<str:act>', checkinvite),
    path('chatroom/checkall/<str:Secret>/<str:act>', checkall),
    path('chatroom/room/<str:Secret>/<str:Eid>', room),
    path('chatroom/room/<str:Secret>/<str:Eid>/<str:Langu>', room),
    path('chatroom/sendmsg', send_messages),
    path('chatroom/loadmsg', load_messages),
    path('chatroom/loadmember/<str:MMid>', load_member),
  
    
    
    path('translator/process_audio/<str:MMid>/<str:Eid>', process_audio),
    path('translator/processtext/<str:MMid>/<str:Eid>', translator_text),
    
    path('employee/list', list_emp),
    path('employee/add', add_emp),
    path('employee/edit/<str:Eid>', edit_emp),
    path('employee/senddata', senddata_emp),
    path("admin/", admin.site.urls),
    path('line/', callback),
    path('line/push/<str:uid>/<str:msg>', sendMsg),
]
