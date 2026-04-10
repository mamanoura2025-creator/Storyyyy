import os
import json
import requests
from flask import Flask, request

# ==============================
# إعدادات البوت
# ==============================

PAGE_ACCESS_TOKEN = "EAAZCWBGJJrWEBRMcXt6YZCJEKDzTKstOXstZAXtCqraCm5MVlwIDLXtLsgd4nLGHuPlnv0wSWLHYyzuIDFHytN6hkYQzoe3GGrBWttPBO7HHC45ZBVExMqkv0n3De4IYUdr2dKstxRnEa8FckFJ3og9d0WOZAsZBY6BuckqNYpYygp3W2ckeXJPzQFZAcuKYZBAu9WsBR1pJ9AZDZD"
VERIFY_TOKEN = "miloud_verify_token"

# ==============================
# البروكسي
# ==============================
proxy = "http://Zr0z0jfj6W20_custom_zone_DZ_st__city_sid_24313775_time_5:2695995@change4.owlproxy.com:7778"
proxies = {
    "http": proxy,
    "https": proxy
}

# ==============================
# الهيدر للذكاء الاصطناعي
# ==============================
headers = {
    "Host": "baithek.com",
    "Content-Type": "application/json",
    "User-Agent": "okhttp/4.9.2"
}

AI_API = "https://baithek.com/chatbee/health_ai/new_health.php"

# ==============================
# ملفات التخزين
# ==============================
USERS_FILE = "users.json"
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w") as f:
        json.dump({}, f)

def load_users():
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(data):
    with open(USERS_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ==============================
# إرسال رسالة لفيسبوك
# ==============================
def send_message(psid, text):
    url = f"https://graph.facebook.com/v18.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {"recipient": {"id": psid}, "message": {"text": text}}
    try:
        r = requests.post(url, json=payload, timeout=15)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"⚠️ خطأ في إرسال الرسالة: {e}")

# ==============================
# الذكاء الاصطناعي
# ==============================
def ask_ai(msg):
    data = {
        "name": "Usama",
        "messages": [{"role": "user", "content": msg}]
    }
    try:
        r = requests.post(
            AI_API,
            headers=headers,
            json=data,
            proxies=proxies,
            timeout=30
        )
        resp_json = r.json()
        return resp_json['choices'][0]['message']['content']
    except Exception as e:
        print("❌ خطأ في AI:", e)
        return "⚠️ حدث خطأ حاول مرة أخرى"

# ==============================
# Flask
# ==============================
app = Flask(__name__)

@app.route("/ping")
def ping():
    return "alive"

@app.route("/webhook", methods=["GET"])
def verify():
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if token == VERIFY_TOKEN:
        return challenge
    return "Error"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    users = load_users()

    for entry in data.get("entry", []):
        for msg in entry.get("messaging", []):
            if "message" not in msg:
                continue

            sender = msg["sender"]["id"]
            text = msg["message"].get("text")
            if not text:
                continue

            if sender not in users:
                users[sender] = {"messages": 0}
                save_users(users)
                welcome = (
                    "👋 أهلا بك في بوت Miloud AI\n\n"
                    "🤖 يمكنك التحدث معي وسأجيبك بالذكاء الاصطناعي.\n"
                    "📌 اكتب أي سؤال للبدء."
                )
                send_message(sender, welcome)

            users[sender]["messages"] += 1
            save_users(users)

            reply = ask_ai(text)
            send_message(sender, reply)

    return "ok"

# ==============================
# تشغيل السيرفر
# ==============================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
