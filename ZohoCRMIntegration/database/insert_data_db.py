from database import db  # Import db from the new database module
from database.schemas import ZohoCreds,Clients,ZohoAudit
from datetime import datetime, timezone,timedelta
from datetime import datetime, timedelta, timezone

def insert_creds(entity_id, access_token, refresh_token,expiration_time):
    """
    Inserts or updates Zoho OAuth tokens for a given user.
    - `entity_id` (unique Key): Unique identifier for the user.
    - `expires_in`: Seconds until token expiry (from Zoho's response).
    """
    with db.session.begin():
        # Check if user already exists (update if yes, else insert)
        existing_creds = db.session.query(ZohoCreds).filter_by(entity_id=entity_id).first()

        if existing_creds:
            # Update existing record
            existing_creds.access_token = access_token
            existing_creds.refresh_token = refresh_token
            existing_creds.expiration_time = expiration_time
        else:
            # Insert new record
            new_creds = ZohoCreds(
                entity_id=entity_id,
                access_token=access_token,
                refresh_token=refresh_token,
                expiration_time=expiration_time,
            )
            db.session.add(new_creds)
        db.session.commit()


def insert_CRM_user(entity_id , users):
    #check if entity_id exists:
    existing_CRM_user = db.session.query(Clients).filter_by(entity_id=entity_id).first()
    if not existing_CRM_user:
        for user in users :
            new_user = Clients(
                    zoho_id=user["id"],
                    entity_id=entity_id,
                    full_name=user['Name']
                )
            db.session.add(new_user)
        db.session.commit()
    else:
        return "USERS already registered"



#here adding mode - one for creating a
def insert_audit_data (entity_id , responses, mode): #repsosne is what you get after you hit the create or update api
    if mode == "create":
        scope = "Created_By"
    elif mode == "update":
        scope = "Modified_By"
    responses = responses["data"]# data key has all the information
    for response in responses:
        new_record = ZohoAudit(
            lead_id = response['details']["id"],
            entity_id = entity_id,
            zoho_id = response['details'][scope]["id"],
            name = response['details'][scope]["name"],
            message = response['message'],
            time = response['details']['Modified_Time']
        )
        db.session.add(new_record)

    db.session.commit()