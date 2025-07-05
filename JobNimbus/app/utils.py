import os
import requests
from flask import current_app


def jobnimbus_headers():
    api_key = current_app.config.get('JOBNIMBUS_API_KEY') or os.getenv("JOBNIMBUS_API_KEY")
    return {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}


def jobnimbus_request(method, url, **kwargs):
    try:
        response = requests.request(method, url, headers=jobnimbus_headers(), **kwargs)
        print(f"JobNimbus API Request - Method: {method}, URL: {url}, Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Text: {response.text[:500]}...")  # Print first 500 chars for debugging
        
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
