import os

from gtts import gTTS
from playsound import playsound

from config import Config

def play_sound(text: str, lang: str):
    tts = gTTS(text, lang=lang)
    filepath = os.path.join(Config.TMP_SAVING_PATH, f'{os.urandom(8).hex()}.mp3')
    tts.save(filepath)
    playsound(filepath, False) 
