from database import db 

from database.schemas import ZohoCreds
from datetime import datetime, timezone, timedelta
import time
def update_zoho_creds(entity_id, tokens):
    access_token = tokens["access_token"]
    current_time = int(time.time())
    existing_creds = db.session.query(ZohoCreds).filter_by(entity_id=entity_id).first()
    if existing_creds:
        # Update existing record
        existing_creds.access_token = access_token
        existing_creds.expiration_time = current_time + 3600
        db.session.commit() #commit the chagnes to database
    else:
        return {"status": "error", "message": "No credentials found for this user"}, 404
