import requests
from flask import current_app

BASE_URL = "https://app.jobnimbus.com/api1"


def get_headers():
    return {
        "accept": "application/json",
        "Authorization": f"Bearer {current_app.config['JOBNIMBUS_API_KEY']}",
        "Content-Type": "application/json",
    }


def create_contact_in_jobnimbus(data):
    response = requests.post(BASE_URL, headers=get_headers(), json=data)
    response.raise_for_status()
    return response.json()


def get_contact_from_jobnimbus(contact_id):
    url = f"{BASE_URL}/{contact_id}"
    response = requests.get(url, headers=get_headers())
    response.raise_for_status()
    return response.json()


def update_contact_in_jobnimbus(contact_id, data):
    url = f"{BASE_URL}/{contact_id}"
    response = requests.put(url, headers=get_headers(), json=data)
    response.raise_for_status()
    return response.json()


def delete_contact_in_jobnimbus(contact_id):
    url = f"{BASE_URL}/{contact_id}"
    response = requests.delete(url, headers=get_headers())
    response.raise_for_status()
    return response.status_code == 204


def get_all_contacts_from_jobnimbus():
    response = requests.get(BASE_URL, headers=get_headers())
    response.raise_for_status()
    return response.json()
