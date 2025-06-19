from fastapi import FastAPI, Request
import requests
import os
from avito_api import get_access_token
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

TEMPLATE = os.getenv("TEMPLATE_MESSAGE", "Здравствуйте! Напишите нам в Telegram 👉 @твой_бот")

@app.post("/webhook")
async def handle_avito_message(request: Request):
    data = await request.json()
    try:
        dialog_id = data['message']['dialog_id']
        sender = data['message']['author']['id']
        token = get_access_token()

        if not token:
            return {"error": "No access token"}

        # 1. Получаем историю сообщений в диалоге
        history_url = f"https://api.avito.ru/messenger/v1/dialogs/{dialog_id}/messages"
        headers = {
            "Authorization": f"Bearer {token}"
        }
        history_response = requests.get(history_url, headers=headers)
        messages = history_response.json().get("messages", [])

        # 2. Проверяем — отвечал ли уже бот
        already_replied = any(msg["author"]["type"] == "user" and msg["author"]["id"] != sender for msg in messages)

        if already_replied:
            return {"status": "already_replied"}

        # 3. Отправляем автоответ
        send_url = f"https://api.avito.ru/messenger/v1/dialogs/{dialog_id}/messages"
        send_headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        payload = {"text": TEMPLATE}
        response = requests.post(send_url, headers=send_headers, json=payload)

        return {"status": "sent", "details": response.text}
    except Exception as e:
        return {"error": str(e)}
