from flask import Flask, request, jsonify
import requests
import traceback
import os

app = Flask(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

FLOWISE_URL = os.environ.get("FLOWISE_URL")

def ask_flowise(question, history=[]):
    try:
        payload = {
            "question": question,
            "chatHistory": history
        }
        print("[PAYLOAD TO FLOWISE]:", payload)

        response = requests.post(FLOWISE_URL, json=payload, timeout=120)
        response.raise_for_status()
        return response.json().get("text", "🤖 Flowise не ответил.")
    except Exception as e:
        print("[ERROR] Flowise call failed:", e)
        return "⚠️ Ошибка при обращении к ИИ. Попробуй позже."

def send_telegram_message(chat_id, text):
    try:
        payload = {
            "chat_id": chat_id,
            "text": text
        }
        response = requests.post(TELEGRAM_API_URL, json=payload)
        response.raise_for_status()
        print("[Telegram OUT]:", response.json())
    except Exception:
        print("[ERROR] Telegram message failed:")
        traceback.print_exc()

@app.route("/webhook", methods=["POST"])
def telegram_webhook():
    try:
        print("[DEBUG] ✅ Telegram Webhook triggered")
        data = request.get_json(force=True)
        message = data.get("message", {})
        chat_id = message.get("chat", {}).get("id")
        text = message.get("text", "").strip()

        print(f"[Telegram IN]: {text}")
        answer = ask_flowise(text)
        send_telegram_message(chat_id, answer)
        return jsonify({"status": "ok", "reply": answer}), 200
    except Exception:
        traceback.print_exc()
        return jsonify({"status": "fail"}), 500

@app.route("/", methods=["GET"])
def root():
    return "Tsunami Telegram Bot is running ✅"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
