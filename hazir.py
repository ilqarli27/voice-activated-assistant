import sounddevice as sd
import vosk
import pyttsx3
import queue
import json
import os
import sys
import numpy as np
import time
import re
import datetime
import threading

from dialogflow_handler import detect_intent_text
from weather import get_weather
from reminder import set_reminder

# -----------------------------
# GOOGLE CREDENTIALS
# -----------------------------
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\user\Downloads\anar-msnx-b3f9b19a7da4.json"

# -----------------------------
# VOSK MODEL
# -----------------------------
model_path = r"C:\Users\user\Downloads\vosk-model-small-en-us-0.15\vosk-model-small-en-us-0.15"
model = vosk.Model(model_path)

# -----------------------------
# TTS SETUP (queue-based, stable)
# -----------------------------
engine = pyttsx3.init()
tts_queue = queue.Queue()

def tts_worker():
    while True:
        text = tts_queue.get()
        if text is None:
            break
        engine.say(text)
        engine.runAndWait()
        tts_queue.task_done()

threading.Thread(target=tts_worker, daemon=True).start()

def speak(text):
    """TTS çağırışı sıraya qoyulur, runtime error olmur"""
    tts_queue.put(text)

# -----------------------------
# AUDIO QUEUE & CALLBACK
# -----------------------------
q = queue.Queue()
def audio_callback(indata, frames, time_info, status):
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))

# -----------------------------
# REAL-TIME ASSISTANT
# -----------------------------
samplerate = 16000
print("Danışın... Assistant yalnız danışıq bitdikdən sonra cavab verəcək (Ctrl+C ilə dayandırın)")

with sd.RawInputStream(samplerate=samplerate, blocksize=8000, dtype='int16',
                       channels=1, callback=audio_callback):

    rec = vosk.KaldiRecognizer(model, samplerate)
    audio_buffer = b""
    last_sound_time = time.time()

    while True:
        data = q.get()
        audio_buffer += data

        # Səs aktivliyi threshold
        audio_np = np.frombuffer(data, dtype=np.int16)
        if np.max(np.abs(audio_np)) > 300:
            last_sound_time = time.time()

        # 1 saniyə səs yoxdursa → danışıq bitdi
        if time.time() - last_sound_time > 1.0 and len(audio_buffer) > 0:
            rec.AcceptWaveform(audio_buffer)
            final_result = json.loads(rec.FinalResult())
            user_text = final_result.get("text", "").strip()
            audio_buffer = b""  # buffer təmizləndi

            if not user_text:
                continue

            print("\nSiz dediniz:", user_text)
            assistant_response = ""

            # -----------------------------
            # Arithmetic (2+2, 5*6)
            try:
                expr = re.findall(r'(\d+\s*[\+\-\*/]\s*\d+)', user_text)
                if expr:
                    result = eval(expr[0])
                    assistant_response = f"The result of {expr[0]} is {result}"
            except:
                pass

            # -----------------------------
            # Weather (sənin weather.py faylına uyğun)
            if "weather" in user_text.lower():
                words = user_text.lower().split()
                city = None
                for pre in ["in", "for"]:
                    if pre in words:
                        idx = words.index(pre)
                        if idx + 1 < len(words):
                            city = " ".join(words[idx+1:]).capitalize()
                            break
                if not city:
                    city = "Warsaw"
                assistant_response = get_weather(city)

            # -----------------------------
            # Reminder (sənin reminder.py faylına uyğun)
            elif "remind me" in user_text.lower():
                remind_time = datetime.datetime.now() + datetime.timedelta(minutes=1)
                assistant_response = set_reminder(user_text, remind_time.strftime("%Y-%m-%d %H:%M"))

            # -----------------------------
            # Dialogflow fallback (online)
            if not assistant_response:
                try:
                    assistant_response = detect_intent_text(
                        project_id="anar-msnx",
                        session_id="user-session",
                        text=user_text
                    )
                except Exception as e:
                    assistant_response = f"Dialogflow error: {str(e)}"

            # -----------------------------
            # Cavabı ekrana və səsə çıxart
            print("Assistant:", assistant_response)
            speak(assistant_response)
