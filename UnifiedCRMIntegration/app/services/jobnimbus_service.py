import os
import requests
from flask import current_app
from app.config import Config

def jobnimbus_headers():
    api_key = current_app.config.get('JOBNIMBUS_API_KEY') or os.getenv("JOBNIMBUS_API_KEY")
    return {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}


def jobnimbus_request(method, endpoint, **kwargs):
    url = f"https://app.jobnimbus.com/api1{endpoint}"
    try:
        response = requests.request(method, url, headers=jobnimbus_headers(), **kwargs)
        try:
            data = response.json()
        except ValueError:
            return {
                "error": "JobNimbus returned non-JSON response",
                "status_code": response.status_code,
                "text": response.text,
            }, response.status_code
        return data, response.status_code
    except Exception as e:
        return {"error": "Failed to contact JobNimbus", "details": str(e)}, 500 