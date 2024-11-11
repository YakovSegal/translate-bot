from google.cloud import speech_v1 as speech
from dotenv import load_dotenv

import requests
import os
import logging
logger = logging.getLogger()

from os.path import join, dirname
load_dotenv(join(dirname(__file__), '.env'))

def speech_to_text(url: str, audio_type: str):
    client = speech.SpeechClient()
    content = requests.get(url).content
    audio = speech.RecognitionAudio(content=content)
    enc = speech.RecognitionConfig.AudioEncoding.OGG_OPUS
    if 'mpeg' in audio_type: enc = speech.RecognitionConfig.AudioEncoding.MP3
    config = speech.RecognitionConfig(
        encoding=enc,
        sample_rate_hertz=16000,
        language_code="he-IL",
        alternative_language_codes=['uk-UK', 'ru-RU']
    )
    response = client.recognize(config=config, audio=audio)
    return get_text(response)

def get_text(response):
    print(response)
    for result in response.results:
        best_alternative = result.alternatives[0]
        transcript = best_alternative.transcript
        return {'text': str(transcript), 'lang_code': str(result.language_code).split('-')[0]}

if __name__ == '__main__':
    print(speech_to_text('https://cdnydm.com/media/K8e_HrPkD-xnKpGQ0fGPFQ.oga'))