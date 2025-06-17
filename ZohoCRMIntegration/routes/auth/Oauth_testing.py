#server side testing file not impporeted in main.py
from flask import Blueprint , Request 
import requests
from config import Config 
import datetime 
from datetime import time ,timedelta,timezone
from database.insert_data_db import insert_creds ,insert_CRM_user
import time 
auth_test = Blueprint('auth_login',__name__)



@auth_test.route("/authorize/<int:entity_id>",methods=["GET"])
def test_creds(entity_id):
    url = "https://accounts.zoho.com/oauth/v2/token"
    #if entity_id  in database reset delete his tokens and reset.

    # Parameters should be sent as form data in the request body
    data = {
        "client_id": Config.client_id,
        "client_secret": Config.client_secret,
        "code": Config.zoho_auth_code,
        "grant_type": "authorization_code",
        "redirect_uri": Config.redirect_uri  # Make sure this matches your Postman setup
    }
    
    # Correct content type header
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    response = requests.post(url, headers=headers, data=data)
    
    if response.status_code == 200:
        access_token = response.json()["access_token"]
        refresh_token = response.json()["refresh_token"]
        expires_in = response.json()["expires_in"]
        current_time = int(time.time())
        expires_in = current_time + expires_in
        # Insert credentials into the database
        insert_creds(
            entity_id,
            access_token, 
            refresh_token, 
            expires_in, #store in UNIX stamp
        )
        #if authoriezed then update the clients table  
        users = requests.get(f"http://127.0.0.1:5000/api/zoho/{entity_id}/users")

        insert_CRM_user(entity_id , users.json())
        return {"status": "success", "data": response.json()}
    else:
        return {"status": "error", "message": response.text}, response.status_code