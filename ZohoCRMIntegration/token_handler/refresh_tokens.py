from database import db 
from database.schemas import ZohoCreds
from datetime import datetime, timezone, timedelta
from config import Config
import requests

ZOHO_ACCOUNTS_URL = "https://accounts.zoho.com"
def refresh_token(entity_id,refresh_token):
    if not entity_id:
        return {"status": "error", "message": "User ID is required"}, 400
    # Fetch the existing credentials from the database
    try:
        url = f"{ZOHO_ACCOUNTS_URL}/oauth/v2/token?refresh_token={refresh_token}&client_id={Config.client_id}&client_secret={Config.client_secret}&grant_type=refresh_token"
        header = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        response = requests.post(url,headers=header)
        if response.status_code == 200:
            data = response.json()
            return data
    except requests.RequestException as e:
        return {"status": "error", "message": str(e)}, 500
    
""""
{
    "access_token": "{new_access_token}",
    "expires_in": 3600,
    "api_domain": "https://www.zohoapis.com",
    "token_type": "Bearer"
}
"""