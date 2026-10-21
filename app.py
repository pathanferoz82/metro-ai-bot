import os
from flask import Flask, request
import openai
import requests

app = Flask(__name__)
VERIFY_TOKEN = "metro123"

@app.route("/")
def home():
    return "METRO AI Bot is Live!"

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        if request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return request.args.get("hub.challenge")
        return "Verification failed", 403
    data = request.get_json()
    try:
        msg = data['entry'][0]['changes'][0]['value']['messages'][0]
        from_number = msg['from']
        msg_text = msg['text']['body']
        client = openai.OpenAI(api_key=os.getenv("OPENAI_KEY"))
        res = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are METRO AI assistant for FK METRO. 5 services: Logo, Website, Video Edit, Visiting Card, Social Post. Hinglish."},
                {"role": "user", "content": msg_text}
            ]
        )
        ai_reply = res.choices[0].message.content
        phone_id = data['entry'][0]['changes'][0]['value']['metadata']['phone_number_id']
        url = f"https://graph.facebook.com/v20.0/{phone_id}/messages"
        headers = {"Authorization": f"Bearer {os.getenv('WHATSAPP_TOKEN')}", "Content-Type": "application/json"}
        payload = {"messaging_product": "whatsapp", "to": from_number, "text": {"body": ai_reply}}
        requests.post(url, headers=headers, json=payload)
    except Exception as e:
        print(e)
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
