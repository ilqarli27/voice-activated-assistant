from flask import Flask, request, jsonify
import os

from speech_to_text import transcribe_speech
from dialogflow_handler import detect_intent_text
from weather import get_weather
from reminder import set_reminder

# -----------------------------
# GOOGLE CREDENTIALS
# -----------------------------
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = (
    r"C:\Users\user\Downloads\anar-msnx-b3f9b19a7da4.json"
)

# -----------------------------
# FLASK APP
# -----------------------------
app = Flask(__name__)

# -----------------------------
# ROUTES
# -----------------------------

@app.route("/")
def home():
    return "Voice-Activated Virtual Assistant backend is running!"

@app.route("/voice", methods=["POST"])
def voice():
    """
    Receives audio (wav) and returns assistant response
    """
    audio_file = request.files.get("audio")
    if not audio_file:
        return jsonify({"error": "No audio file uploaded"}), 400

    # 1️⃣ Speech → Text
    audio_bytes = audio_file.read()
    user_text = transcribe_speech(audio_bytes)

    if not user_text:
        return jsonify({
            "response": "I could not understand your audio."
        })

    # 2️⃣ Dialogflow Intent Detection
    try:
        response_text = detect_intent_text(
            project_id="anar-msnx",   # 🔴 BURANI Dialogflow Project ID ilə EYNİ ET
            session_id="user-session",
            text=user_text
        )
    except Exception as e:
        response_text = f"Dialogflow error: {str(e)}"

    # 3️⃣ Weather intent (fallback / custom logic)
    if "weather" in user_text.lower():
        words = user_text.lower().split()
        city = None
        if "in" in words:
            idx = words.index("in")
            if idx + 1 < len(words):
                city = words[idx + 1].capitalize()
        if not city:
            city = "Baku"
        response_text = get_weather(city)

    # 4️⃣ Reminder intent
    if "remind me" in user_text.lower():
        response_text = set_reminder(user_text)

    return jsonify({
        "transcribed_text": user_text,
        "response": response_text
    })

# -----------------------------
# RUN SERVER
# -----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
