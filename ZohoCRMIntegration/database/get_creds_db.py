from database import db
from database.schemas import ZohoCreds
from token_handler.refresh_tokens import refresh_token
from datetime import datetime, timezone
from flask import current_app as app
def get_zoho_creds(entity_id: int) -> dict | None:
    """Fetches the latest Zoho credentials from the database and returns them as a dictionary."""
    try:
        creds = db.session.query(ZohoCreds).filter_by(entity_id=entity_id).first()
        if creds is None:
            return None
        return {
            "access_token": creds.access_token,
            "refresh_token": creds.refresh_token,
            "expiration_time": creds.expiration_time,
        }
    except Exception as e:
        app.logger.error(f"Database error while fetching Zoho creds: {e}")
        return None



#what the get_zoho_Creds will retirn 
"""
somethign like this
{
    "access_token": "abc123",
    "refresh_token": "xyz789",
    "expiration_time": "UNIX timestamp",
}
"""