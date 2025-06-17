from flask import Blueprint, request, redirect,session
import requests
from config import Config 
import datetime 
from datetime import time ,timedelta,timezone
from database.insert_data_db import insert_creds ,insert_CRM_user
from database.get_creds_db import get_zoho_creds
import time 
auth_blueprint = Blueprint('authorization',__name__)

#ussing seesion to store remodel id temporarily
ZOHO_REDIRECT_URI="http://localhost:5000/zoho/authorize/callback"
ZOHO_ACCOUNTS_URL = "https://accounts.zoho.com"

@auth_blueprint.route("/<int:entity_id>/redirect",methods=["GET"])
def creds(entity_id):
    #check if user creds availabe in credentials table . 
    creds = get_zoho_creds(entity_id)
    if creds:
        return "user aldready Authorized"
    #if entity_id  in database reset delete his tokens and reset.
    session['entity_id'] = entity_id
    auth_url = (
        "https://accounts.zoho.com/oauth/v2/auth"
        "?scope=ZohoCRM.users.ALL,ZohoCRM.modules.ALL"
        f"&client_id={Config.client_id}"
        f"&response_type=code"
        f"&access_type=offline"
        f"&redirect_uri={ZOHO_REDIRECT_URI}"
    )
    return redirect(auth_url)
    
@auth_blueprint.route("/callback")
def callback():
    entity_id = session.get('entity_id')
    code = request.args.get("code")
    accounts_server = request.args.get("accounts-server")
    # Exchange grant code for access token
    token_url = f"{accounts_server}/oauth/v2/token"
    data = {
        "client_id": Config.client_id,
        "client_secret": Config.client_secret,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": ZOHO_REDIRECT_URI
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    response = requests.post(token_url, headers=headers, data=data)
    
    if response.status_code == 200:
        access_token = response.json()["access_token"]
        refresh_token = response.json()["refresh_token"]
        expires_in = response.json()["expires_in"]
        current_time = int(time.time())
        expires_in = current_time + expires_in
        # Insert credentials into the database
        insert_creds(
            entity_id= entity_id,
            access_token=access_token, 
            refresh_token=refresh_token, 
            expiration_time=expires_in, #store in UNIX stamp
        )
        users = requests.get(f"http://127.0.0.1:5000/api/zoho/{entity_id}/users")
        try:
            user_data = users.json()
        except Exception:
            return {"status": "error", "message": "Invalid user response"}

        insert_CRM_user(entity_id, user_data)

        return {"status": "success", "message": "authorization Successful"}
    else:
        return {"status": "error", "message": response.text}, response.status_code

    