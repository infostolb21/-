import os
import requests
from dotenv import load_dotenv

load_dotenv()

def get_access_token():
    url = "https://api.avito.ru/token/"
    data = {
        "grant_type": "client_credentials",
        "client_id": os.getenv("AVITO_CLIENT_ID"),
        "client_secret": os.getenv("AVITO_CLIENT_SECRET")
    }

    response = requests.post(url, data=data)

    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        print("Ошибка при получении токена:", response.text)
        return None
