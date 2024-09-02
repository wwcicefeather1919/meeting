from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.shortcuts import redirect
import io
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os
import logging
from datetime import datetime
from django.conf import settings  #驗證有無產生錄音檔是：結果是正常
import glob
import whisper
from deep_translator import GoogleTranslator
import sys
import traceback
import librosa
import soundfile as sf
# 引入資料庫連接
from django.db import connection
# 時間庫
from datetime import datetime


# from django.http import JsonResponse

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 加载 Whisper 模型（可以选择不同大小的模型，如 'tiny', 'base', 'small', 'medium', 'large'）
model = whisper.load_model("medium", download_root=r"[輸入模組存放位置]")
# Create your views here.

@csrf_exempt
def process_audio(request,MMid,Eid):
    if request.method == 'POST':
        translations = {
            'tw': {'dest': 'chinese (traditional)', 'prefix': 'TW'},
            'en': {'dest': 'english', 'prefix': 'EN'}
        }
        
        audio_file = request.FILES['audio']
        
        # 生成唯一的文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"audio_{timestamp}.wav"
        processed_filename = f"processed_{timestamp}.wav"
        transcript_filename = f"transcript_{timestamp}.txt"
        
        # 保存音频文件
        file_path = os.path.join(settings.MEDIA_ROOT, filename)
        with open(file_path, 'wb+') as destination:
            for chunk in audio_file.chunks():
                destination.write(chunk)
        
        logger.info(f"音頻文件已保存: {file_path}")

        try:
            # 使用 librosa 加载并重采样音频
            audio, sr = librosa.load(file_path, sr=16000, mono=True)
            
            # 保存处理后的音频
            processed_file_path = os.path.join(settings.MEDIA_ROOT, processed_filename)
            sf.write(processed_file_path, audio, sr, subtype='PCM_16')
            
            logger.info(f"處理後的音頻文件已保存: {processed_file_path}")
            
            # 使用 Whisper 進行轉錄
            result = model.transcribe(file_path)
            transcript = result["text"]
            
            logger.info(f"轉錄結果：{transcript}")
            
            if transcript:
                now = datetime.now()
                with connection.cursor() as cursor:
                    cursor.execute("insert into meeting_chatroom_main(NDate,MMid,Eid,message) values (%s,%s,%s,%s)",[now,MMid,Eid,transcript])
                    MCMid = cursor.lastrowid
                    
                    result = translator_text(MMid,MCMid,transcript)
                
                for lang, info in translations.items():
                    try:
                        translator = GoogleTranslator(source='auto', target=info['dest'])
                        chunks = [transcript[i:i+1000] for i in range(0, len(transcript), 1000)]
                        translated_chunks = [translator.translate(chunk) for chunk in chunks]
                        translation = ''.join(translated_chunks)
                        
                        if translation:
                            with connection.cursor() as cursor:
                                #新增翻譯後的資料
                                cursor.execute("insert into meeting_chatroom_version(MMid,MCMid,Lange,Contents) values (%s,%s,%s,%s)",[MMid,MCMid,lang,translation])
                        else:
                            logger.error(f"{info['prefix']} 翻譯结果為空")
                    except Exception as e:
                        logger.error(f"{info['prefix']} 翻譯過程中出錯: {str(e)}")
                        logger.error(f"錯誤類型: {type(e).__name__}")
                        logger.error(f"錯誤詳情: {str(e)}")
                        logger.error(f"錯誤堆棧: {traceback.format_exc()}")
            else:
                logger.error(f"音訊擷取，结果為空")
            
            return JsonResponse({
                'success': True, 
                'transcript': transcript, 
                'timestamp': timestamp
            })
        except Exception as e:
            logger.error(f"轉錄過程中出錯: {str(e)}")
            return JsonResponse({
                'success': False, 
                'error': str(e)
            })


def translator_text(MMid,MCMid,msg):
    translations = {
        'tw': {'dest': 'chinese (traditional)', 'prefix': 'TW'},
        'en': {'dest': 'english', 'prefix': 'EN'}
    }
    for lang, info in translations.items():
        try:
            translator = GoogleTranslator(source='auto', target=info['dest'])
            chunks = [msg[i:i+1000] for i in range(0, len(msg), 1000)]
            translated_chunks = [translator.translate(chunk) for chunk in chunks]
            translation = ''.join(translated_chunks)
            
            if translation:
                with connection.cursor() as cursor:
                    #新增翻譯後的資料
                    cursor.execute("insert into meeting_chatroom_version(MMid,MCMid,Lange,Contents) values (%s,%s,%s,%s)",[MMid,MCMid,lang,translation])
            else:
                logger.error(f"{info['prefix']} 翻譯结果為空")
        except Exception as e:
            logger.error(f"{info['prefix']} 翻譯過程中出錯: {str(e)}")
            logger.error(f"錯誤類型: {type(e).__name__}")
            logger.error(f"錯誤詳情: {str(e)}")
            logger.error(f"錯誤堆棧: {traceback.format_exc()}")
    return 'ok'
    


test_translator = GoogleTranslator(source='chinese (traditional)', target='english')
test_result = test_translator.translate("你好，世界")
logger.info(f"測試翻譯結果: {test_result}")
