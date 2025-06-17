import os
import requests
from app.config import Config

def jobnimbus_headers():
    return {"Authorization": f"Bearer {Config.JOBNIMBUS_API_TOKEN}", "Content-Type": "application/json"}

def jobnimbus_request(method, url, **kwargs):
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