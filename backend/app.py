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
from difflib import get_close_matches

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
# TTS SETUP (thread-safe)
# -----------------------------
tts_queue = queue.Queue()
engine = pyttsx3.init()
tts_lock = threading.Lock()

def tts_worker():
    while True:
        text = tts_queue.get()
        if text is None:
            break
        with tts_lock:
            engine.say(text)
            engine.runAndWait()
        tts_queue.task_done()

threading.Thread(target=tts_worker, daemon=False).start()

def speak(text):
    tts_queue.put(text)

# -----------------------------
# AUDIO CALLBACK
# -----------------------------
audio_queue = queue.Queue()
def audio_callback(indata, frames, time_info, status):
    if status:
        print(status, file=sys.stderr)
    audio_queue.put(bytes(indata))

# -----------------------------
# City correction (weather.py dəyişməz qalır)
# -----------------------------
known_cities = ["Warsaw", "London", "Paris", "Berlin", "New York", "Moscow", "Tokyo", "Istanbul", "Baku"]

def correct_city_name(city):
    match = get_close_matches(city, known_cities, n=1, cutoff=0.6)
    if match:
        return match[0]
    return city

# -----------------------------
# REAL-TIME ASSISTANT LOOP
# -----------------------------
samplerate = 16000
print("Danışın... Assistant cavabları real-time olaraq çıxacaq (Ctrl+C ilə dayandırın)")

rec = vosk.KaldiRecognizer(model, samplerate)
audio_buffer = b""
last_sound_time = time.time()

# Stream-i ayrıca saxlayırıq ki, Ctrl+C işləsin
stream = sd.RawInputStream(samplerate=samplerate, blocksize=8000,
                           dtype='int16', channels=1, callback=audio_callback)
stream.start()

try:
    while True:
        try:
            data = audio_queue.get(timeout=0.1)
        except queue.Empty:
            continue
        audio_buffer += data

        audio_np = np.frombuffer(data, dtype=np.int16)
        if np.max(np.abs(audio_np)) > 300:
            last_sound_time = time.time()

        # 0.8 saniyə silence → danışıq bitdi
        if time.time() - last_sound_time > 0.8 and len(audio_buffer) > 0:
            rec.AcceptWaveform(audio_buffer)
            final_result = json.loads(rec.FinalResult())
            user_text = final_result.get("text", "").strip()
            audio_buffer = b""

            if not user_text:
                continue

            print("\nSiz dediniz:", user_text)
            assistant_response = ""

            # -----------------------------
            # Arithmetic
            try:
                expr = re.findall(r'(\d+\s*[\+\-\*/]\s*\d+)', user_text)
                if expr:
                    result = eval(expr[0])
                    assistant_response = f"The result of {expr[0]} is {result}"
            except:
                pass

            # -----------------------------
            # Weather intent
            if re.search(r'\b(weather|temperature|forecast)\b', user_text, re.IGNORECASE):
                city = None
                matches = re.findall(r"(?:forecast for|weather in|in|for)\s+([A-Za-z\s]+)", user_text, re.IGNORECASE)
                if matches:
                    city = correct_city_name(matches[-1].strip())  # son uyğunluğu city kimi götür
                if not city:
                    city = "Warsaw"
                try:
                    assistant_response = get_weather(city)
                    if "not available" in assistant_response.lower():
                        assistant_response = f"Offline: Cannot fetch live weather for {city}, sorry!"
                except:
                    assistant_response = f"Offline: Cannot fetch weather for {city}."

            # -----------------------------
            # Reminder intent
            elif re.search(r'\b(remind|reminder)\b', user_text, re.IGNORECASE):
                remind_time = datetime.datetime.now() + datetime.timedelta(minutes=1)
                try:
                    assistant_response = set_reminder(user_text, remind_time.strftime("%Y-%m-%d %H:%M"))
                except:
                    assistant_response = "Unable to set reminder."

            # -----------------------------
            # Dialogflow fallback
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

except KeyboardInterrupt:
    print("\nAssistant dayandırıldı.")
finally:
    stream.stop()
    stream.close()
    tts_queue.put(None)  # TTS thread-i dayandır
