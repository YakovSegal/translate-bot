import six
from google.cloud import translate_v2 as translate

import logging
import coloredlogs

import traceback
import os
from os.path import dirname, join
from dotenv import load_dotenv
import re
from langdetect import detect

try:
    from TranslateBot.maytapi_helper import Client
    from TranslateBot.speech import speech_to_text
    from TranslateBot.yemot import send_bot
except:
    print(traceback.format_exc())
    from maytapi_helper import Client
    from speech import speech_to_text

load_dotenv(join(dirname(__file__), '.env'))

coloredlogs.install(level="DEBUG")
logger = logging.getLogger(__file__)
handler = logging.FileHandler('/opt/server/TranslateBot/bot.log')
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)

from threading import Thread

def translate_text(target, text):
    translate_client = translate.Client()
    if isinstance(text, six.binary_type):
        text = text.decode("utf-8")
    result = translate_client.translate(text, target_language=target)
    return result["translatedText"]


def bot(update):
    try:
        update_type = update["type"]
        if update_type == "ack":
            return {"success": True, "message": "This Is ack update type"}
        if 'user' not in update: return {'success': False, 'message': 'user not in update'}
        pid = update["product_id"]
        phone_id = update["phone_id"]
        message = update["message"]
        user = update["user"]
        bot_phone = update["receiver"]
        time_stamp = update["timestamp"]
        update_type = update["type"]
        reply = update["reply"]
        message_type = message["type"]
        if message_type == 'text':
            text = message["text"]
        message_id = message["id"]
        fromMe = message["fromMe"]

        user_id = user["id"]
        name = user["name"]
        phone = user["phone"]
        conversation = update["conversation"]
        chat_is_personal = 'participants' not in update
        chat_is_group = 'participants' in update

        try:
            button = message['payload']
            logger.info(f'bot auto: {phone} selected button:  {button}')
        except KeyError:
            button = None

        

        bot = Client(phone_id=phone_id, product_id=pid, api_token=os.environ.get('X_MAYTAPI_KEY'))

        if chat_is_group: # and conversation not in ['120363027378528948@g.us']:
            if message_type in ['ptt', 'ogg', 'audio', 'oga', 'opus']:
                stt = speech_to_text(message['url'], audio_type=message['mime'])

                txt = stt['text']
                txt_lang = stt['lang_code']
                if txt_lang != 'he': target = 'he'
                elif txt_lang == 'he': target = 'ru'
                else:
                    hl = re.compile(r'אבגדהוזחטיכלמנסעפצקרשתךףץםן')
                    if hl.match(txt):
                        target = 'ru'
                    else:
                        target = 'he'

                msg = translate_text(target, txt)

                bot.send_message(conversation, msg, reply_to=message_id)

            elif message_type == 'text':
                txt_lang = detect(text)
                if txt_lang in ['uk', 'ru']:
                    target = 'he'
                elif txt_lang == 'he':
                    target = 'ru'
                else:
                    hl = re.compile(r'אבגדהוזחטיכלמנסעפצקרשתךףץםן')
                    if hl.match(text):
                        target = 'ru'
                    else:
                        target = 'he'
                msg = translate_text(target, text)
                bot.send_message(conversation, msg, reply_to=message_id)
                        
                return {'success': True, 'msg': msg}
            return {'success': False, 'message': f'group chat but {message_type} message type is not allowed'}
        
        else:
            if text.startswith('דףיומי'):
                if phone in ['972547852182', '972548407906']:
                    date = text.split(' ')[-1]
                    logger.info(f'receiving date {date}')
                    tr = Thread(target=send_bot, kwargs={'date': date, 'phone': '0504171782', 'conversation': conversation})
                    tr.start()
                    tr.join()
                    #async def task(): send_bot(date, '0504171782', conversation=conversation)
                    #asyncio.create_task(task())
                    

            if button is None: return {'1':'1'}
            
            date = button.split(':')[-1]
            if 'all' in button: res = send_bot(date, '0504171782')
            elif 'voice' in button: res = send_bot(date, '0504171782', send_text=False, send_files=False)
            elif 'files' in button: res = send_bot(date, '0504171782', send_text=False, send_voice=False)
            elif 'text' in button: res = send_bot(date, '0504171782', send_files=False, send_voice=False)
            bot.send_message(conversation, str(res), reply_to=message_id)
            return {'success': True, 'msg': 'private chat is not allowed'}
    except:
        logger.error(traceback.format_exc())
        return {'success': False, 'msg': traceback.format_exc()}


if __name__ == '__main__':
    result = translate_text('ru', 'שלום מה קורה')
    print(result)