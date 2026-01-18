# voice-activated-assistant
🔥 VOICE-ACTIVATED VIRTUAL ASSISTANT
TAM ARDICILLIQ (BAŞDAN AXIRA)
1️⃣ PROJECT SETUP & STRUCTURE

Harada: Lokal (VS Code)

Python project açılır

Folder strukturu yaradılır

requirements.txt hazırlanır

👉 Bu mərhələ olmadan heç nəyə başlanmır

2️⃣ GOOGLE CLOUD – SPEECH-TO-TEXT

Harada: Google Cloud Console

Project yaradılır

Speech-to-Text API aktiv edilir

Service account key alınır

Local environment-a bağlanır

👉 Səs → Text çevrilməsi təmin olunur

3️⃣ VOICE INPUT → TEXT (LOCAL TEST)

Harada: Python

Mikrofon input oxunur

Google API-yə göndərilir

Çıxışda plain text alınır

👉 Bu mərhələ 100% işləməlidir, yoxsa davam edilmir

4️⃣ DIALOGFLOW AGENT (NLP)

Harada: Dialogflow Console

Agent yaradılır

Intents:

SetReminder

GetWeather

SendMessage

Entities:

time

date

message

👉 Text → Intent + Data

5️⃣ FLASK BACKEND (LOGIC KÖPRÜSÜ)

Harada: Python (Flask)

Flask server qurulur

Dialogflow webhook endpoint yaradılır

Intent-lər backend-də qarşılanır

👉 NLP ilə real logic arasında körpü

6️⃣ DATABASE (SQLITE)

Harada: SQLite

reminders table

messages table

logs table

👉 Məlumatların saxlanması təmin olunur

7️⃣ SERVICES (TASK LOGIC)

Harada: Python

Reminder service

Weather service

Message handling

👉 Intent → Action

8️⃣ FULL PIPELINE INTEGRATION

ƏN VACİB MƏRHƏLƏ

Mikrofon
 ↓
Speech-to-Text
 ↓
Text
 ↓
Dialogflow
 ↓
Intent + Entities
 ↓
Flask Backend
 ↓
Database / Weather
 ↓
Text Response


👉 Bu nöqtədə system artıq işləyir

9️⃣ TEXT-TO-SPEECH (ƏLAVƏ, AMMA GÜCLÜ)

Harada: Google Text-to-Speech

Backend response səsə çevrilir

Assistant cavabları danışır

👉 Real “virtual assistant” effekti

🔟 CONTEXT MANAGEMENT (SMART NLP)

Harada: Dialogflow

Context-lər əlavə olunur

Multi-step conversation mümkün olur

👉 Assistant daha ağıllı görünür

1️⃣1️⃣ ERROR HANDLING & FALLBACK

Harada: Hər layer

Speech error

Intent error

Missing info

👉 “Başa düşmədim” halları idarə olunur

1️⃣2️⃣ LOGGING & HISTORY

Harada: SQLite

Command history

Error logs

👉 Debug + report üçün

1️⃣3️⃣ SIMPLE UI (OPSİONAL)

Harada: HTML + Flask

Mic button

Response display

👉 Demo üçün
