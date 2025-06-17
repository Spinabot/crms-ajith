#only for development use this retursn all the fields names for particular module
from flask import Blueprint, request 
import requests
from token_handler.tokens import fetch_tokens
meta_blueprint = Blueprint("metadata",__name__)


@meta_blueprint.route("/<int:entity_id>/leads/meta",methods = ['GET'])
def meta_data(entity_id):
    module = request.args.get('module', 'Leads')  # Default to 'Leads' if not provided
    type = request.args.get('type', 'all')  # Default to 'all' if not provided
    url = "https://www.zohoapis.com/crm/v8/settings/fields"
    token = fetch_tokens(entity_id)
    params = {
        "module": module,
        "type": type
    }
    header = {"Authorization":"Zoho-oauthtoken "+token["access_token"]}
    response = requests.get(url,params=params,headers = header)
    if response.status_code == 200:

        return {"status":"Success","data":response.json()}
    else:
        return {"status":"failure", "message":"error getting metadata","status_code":response.status_code}