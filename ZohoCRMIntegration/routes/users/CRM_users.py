from flask import current_app as app 
from flask import Blueprint
from token_handler.tokens import fetch_tokens
import requests
from utils.extension import limiter
zoho_users_blueprint = Blueprint("zoho_users",__name__)


@zoho_users_blueprint.route("/<int:entity_id>/users")
@limiter.limit("3 per minute")
def get_user(entity_id):
    print("fetching Users")
    token = fetch_tokens(entity_id)
    access_token = token["access_token"]
    print(access_token)
    url = "https://www.zohoapis.com/crm/v8/users?type=AdminUsers"
    header = {"Authorization":"Zoho-oauthtoken "+ access_token}
    response = requests.get(url,headers=header)
    if response.status_code == 200:
        users = response.json()["users"]
        total_users = []
        for user in users :
            total_users.append( {
                "id":user['id'],
                "Name":user['full_name'],
                "email":user["email"]
            })
        return total_users

    else:
        return {"message":"Could not retrieve user details"},response.status_code
    