from datetime import datetime
from typing import Dict
from typing import List
from typing import Optional

from pydantic import BaseModel

# these are pydantic models schema and not the database models


class Client(BaseModel):
    access_token: str
    refresh_token: str
    extracted_time: datetime


class ClientCreateData(BaseModel):
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    companyName: Optional[str] = None
    emails: Optional[List[Dict]] = None
    phones: Optional[List[Dict]] = None
    billingAddress: Optional[Dict] = None


class UpdateClientData(BaseModel):
    clientId: str
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    companyName: Optional[str] = None
    emailsToAdd: Optional[List[Dict]] = None
    phonesToAdd: Optional[List[Dict]] = None
    emailsToEdit: Optional[List[Dict]] = None
    phonesToEdit: Optional[List[Dict]] = None
    billingAddress: Optional[Dict] = None
    phonesToDelete: Optional[List[str]] = None
    emailsToDelete: Optional[List[str]] = None


class ArchiveClientData(BaseModel):
    clientId: str
