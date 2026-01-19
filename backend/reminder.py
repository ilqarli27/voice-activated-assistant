import json
import os
  # main.py-dakı speak funksiyasını istifadə etmək üçün
from tts import speak


REMINDER_FILE = "reminders.json"

def set_reminder(text, remind_time):
    reminders = []
    if os.path.exists(REMINDER_FILE):
        with open(REMINDER_FILE, "r") as f:
            reminders = json.load(f)
    
    reminders.append({"text": text, "time": remind_time})
    with open(REMINDER_FILE, "w") as f:
        json.dump(reminders, f)
    return f"Reminder set: {text} at {remind_time}"

def check_reminders():
    import datetime
    now = datetime.datetime.now()
    if os.path.exists(REMINDER_FILE):
        with open(REMINDER_FILE, "r") as f:
            reminders = json.load(f)
        new_reminders = []
        for r in reminders:
            r_time = datetime.datetime.strptime(r["time"], "%Y-%m-%d %H:%M")
            if now >= r_time:
                print("Reminder:", r["text"])
                speak(f"Reminder: {r['text']}")
            else:
                new_reminders.append(r)
        with open(REMINDER_FILE, "w") as f:
            json.dump(new_reminders, f)

