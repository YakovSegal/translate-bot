import requests
import json
from datetime import datetime
import os
from os.path import join, dirname, abspath
try: 
    from TranslateBot.maytapi_helper import Client
    from TranslateBot.shas import get_index
except: 
    from maytapi_helper import Client
    from shas import get_index

import base64
from pydub import AudioSegment
import traceback
import logging, coloredlogs

coloredlogs.install(level="DEBUG")
logger = logging.getLogger(__file__)
handler = logging.FileHandler('/opt/server/TranslateBot/bot.log')
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)
logging.getLogger('urllib3').setLevel(logging.INFO)
converter_logger = logging.getLogger("pydub.converter")
converter_logger.addHandler(handler)

username = '029990222' #'0795140000' #"033081679" 
password = '2727' #'052764' #"1235" 
path = 'ivr2:/1/09/99/1/2' #'ivr2:/5' 


def GetSession(token):
    url = f"https://www.call2all.co.il/ym/api/Login?GetSession={token}"
    r = requests.get(url)
    return r.status_code

def get_token(username,password,token):
    if token == "token":
        url = f"https://www.call2all.co.il/ym/api/Login?username={username}&password={password}"
        r = requests.get(url)
        return json.loads(r.text)["token"]
    if GetSession(token) == 200 :
        return token
    else:
        url = f"https://www.call2all.co.il/ym/api/Login?username={username}&password={password}"
        r = requests.get(url)
        return json.loads(r.text)["token"]

def Logout(token):
    url = f"https://www.call2all.co.il/ym/api/Logout?token={token}"
    r = requests.get(url)
    print ("log out => ")
    print (json.loads(r.text))
    return True

def DownloadFile(token,path, filename):
    url = f"https://www.call2all.co.il/ym/api/DownloadFile?token={token}&path={path}"
    r = requests.get(url)
    with open(abspath(join('/opt/files/', filename)), 'wb') as f:
        f.write(r.content)
    return filename

def get_file_url(phone: str):
    token = get_token(username,password,'token')
    res = requests.get(f'https://www.call2all.co.il/ym/api/GetIVR2Dir?token={token}&path=/1/5/2/1/2&orderDir=desc').json()
    #print(res)
    for file in res['files']:
        if file['phone'] == phone:
            path = file['what']
            break
    if path is None: 
        print('missing "path"')
        return 'error'
    filename = path.split('/')[-1]
    return DownloadFile(token, path, f"{filename}") # 'https://yakovsegal.ovh/files/' +  

def send_bot(date: str, phone: str, conversation: str = None, send_files: bool = True, send_voice: bool=True, send_text: bool=True):
    try:
        bot = Client(phone_id='23755', product_id='c8b8c8a7-4147-47ad-b727-5e69a0842a59',api_token='5c493d48-00df-4cb0-9d68-d5ffb1de4365')
        if conversation: 
            groups = [conversation]
            bot.send_message(conversation, f'מחפש קובצי שמע לתאריך {date} מאת {phone}')
        else: groups = ['97225943121-1614774754@g.us', '120363027378528948@g.us']
        #groups = ['']
        url = get_file_url(phone)
        logger.debug(url)
        
        if url == 'error':
            if conversation: bot.send_message(conversation, f'לא נמצאו קבצי שמע')
            return 
        if conversation: bot.send_message(conversation, f'נמצא קובץ שמע: {url}')

        to_calc = datetime.strftime(datetime.strptime(date, '%d-%m-%Y'), '%Y-%m-%d')
        day_page_base = requests.get(f'https://www.hebcal.com/hebcal?cfg=json&v=1&F=on&start={to_calc}&end={to_calc}').json()['items'][0]['hebrew']
        day_page = day_page_base.replace('״', '').replace('"', '').replace("'", '').replace("`", '').replace('דף ', '').replace('׳','')
        logger.debug('day_page %s', day_page)
        day_page_a = get_index(day_page + ' א')
        day_page_a_pdf = f'https://daf-yomi.com/Data/UploadedFiles/DY_Page/{day_page_a}.pdf'
        day_page_b = get_index(day_page + ' ב')
        day_page_b_pdf = f'https://daf-yomi.com/Data/UploadedFiles/DY_Page/{day_page_b}.pdf'
        he_date = requests.get(f'https://www.hebcal.com/converter?cfg=json&date={to_calc}&g2h=1&strict=1').json()['heDateParts']
        wav_file_path = '/opt/files/' + url
        ogg_file_path = '/opt/files/' + url.strip('.wav') + '.opus'
        logger.debug('ogg_file_path: %s', ogg_file_path)

        if conversation: bot.send_message(conversation, f'קובצי PDF:\n*{day_page_a}*\n{day_page_a_pdf}\n*{day_page_b}*\n{day_page_b_pdf}')

        logger.debug('compressing file to bitrate 8k')
        if conversation: bot.send_message(conversation, f'מתבצע כיווץ לקובץ שמע {url}\nהפעולה עשויה לארוך מספר דקות')
        song = AudioSegment.from_file(wav_file_path, codec='opus')
        compressing = song.export(ogg_file_path, format="opus", bitrate="8k")
        logger.debug('compressing: %s', compressing)
        logger.debug('comressing complete')
        if conversation: bot.send_message(conversation, f'הכיווץ הושלם')
        
        with open(ogg_file_path, "rb") as img_file:
            b64_string = base64.b64encode(img_file.read())
            firstStr = "data:audio/ogg; codecs=opus;base64,"
            formatImg = b64_string.decode('utf-8')
            fullDataImg = firstStr+formatImg
        for group in groups:
            if send_voice:
                res = bot.send_audio(group, fullDataImg, file_name=ogg_file_path.split('/')[-1])
                logger.debug(res)
            if send_files:
                res = bot.send_file(group, day_page_a_pdf, file_name=day_page + ' א' + '.pdf')
                logger.debug(res)
                res = bot.send_file(group, day_page_b_pdf, file_name=day_page + ' ב' + '.pdf')
                logger.debug(res)

            if send_text:
                res = bot.send_message(group, """
*"א גישמאק היומי"*
דף היומי ל {} ב{} {}
מסכת {}
*שמעו ותחי נפשכם*
                """.format(he_date['d'], he_date['m'], he_date['y'], day_page_base))
                logger.debug(res)
        
        if conversation:
            bot.send_message_buttons(conversation, 'יש לבחור פעולה', [{'id': f'voice:{date}', 'text': 'שלח קולי בלבד'},{'id': f'files:{date}', 'text': 'שלח קבצים בלבד'},{'id': f'all:{date}', 'text': 'שלח הכל'}])
            bot.send_message_buttons(conversation, 'יש לבחור פעולה', [{'id': f'text:{date}', 'text': 'שלח טקסט בלבד'}])

    except:
        logger.error(traceback.format_exc())
        if not conversation:
            bot.send_message('972547852182', '```' + traceback.format_exc() + '```')
        else:
            bot.send_message_buttons(conversation, '```' + traceback.format_exc() + '```\n' + 'יש לבחור פעולה', [{'id': f'voice:{date}', 'text': 'שלח קולי בלבד'},{'id': f'files:{date}', 'text': 'שלח קבצים בלבד'},{'id': f'all:{date}', 'text': 'שלח הכל'}])
            bot.send_message_buttons(conversation, 'יש לבחור פעולה', [{'id': f'text:{date}', 'text': 'שלח טקסט בלבד'}])

def send_call(token, phone):
    res = requests.get(f'https://www.call2all.co.il/ym/api/CreateTemplate?token={token}&description={phone}').json()
    print(res)
    template = res['templateId']
    res = requests.get(f'https://www.call2all.co.il/ym/api/UpdateTemplateEntry?token={token}&templateId={template}&phone={phone}&name={phone}&moreinfo={phone}&blocked=0')
    print(res.json())
    res = requests.get(f'https://www.call2all.co.il/ym/api/RunCampaign?token={token}&templateId={template}')
    print(res.json())
    res = requests.get(f'https://www.call2all.co.il/ym/api/DeleteTemplate?token={token}&templateId={template}')
    print(res.json())

if __name__ == '__main__':
    send_bot('20-07-2023', '0504171782', '972547852182')
    #send_call('0799414082:12345678', '0547852182')