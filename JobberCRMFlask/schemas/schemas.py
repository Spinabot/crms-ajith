from datetime import datetime
from typing import Dict, List, Optional
from marshmallow import Schema, fields, ValidationError

# Base schema class for validation
class BaseSchema(Schema):
    pass

class ClientSchema(BaseSchema):
    access_token = fields.Str(required=True)
    refresh_token = fields.Str(required=True)
    extracted_time = fields.DateTime(required=True)

class ClientCreateDataSchema(BaseSchema):
    firstName = fields.Str(allow_none=True)
    lastName = fields.Str(allow_none=True)
    companyName = fields.Str(allow_none=True)
    emails = fields.List(fields.Dict(), allow_none=True)
    phones = fields.List(fields.Dict(), allow_none=True)
    billingAddress = fields.Dict(allow_none=True)

class UpdateClientDataSchema(BaseSchema):
    clientId = fields.Str(required=True)
    firstName = fields.Str(allow_none=True)
    lastName = fields.Str(allow_none=True)
    companyName = fields.Str(allow_none=True)
    emailsToAdd = fields.List(fields.Dict(), allow_none=True)
    phonesToAdd = fields.List(fields.Dict(), allow_none=True)
    emailsToEdit = fields.List(fields.Dict(), allow_none=True)
    phonesToEdit = fields.List(fields.Dict(), allow_none=True)
    billingAddress = fields.Dict(allow_none=True)
    phonesToDelete = fields.List(fields.Str(), allow_none=True)
    emailsToDelete = fields.List(fields.Str(), allow_none=True)

class ArchiveClientDataSchema(BaseSchema):
    clientId = fields.Str(required=True)

# Helper functions to convert between dict and schema objects
def validate_client_create_data(data):
    """Validate client create data using marshmallow schema."""
    schema = ClientCreateDataSchema()
    try:
        validated_data = schema.load(data)
        return validated_data
    except ValidationError as e:
        raise ValueError(f"Validation error: {e.messages}")

def validate_update_client_data(data):
    """Validate update client data using marshmallow schema."""
    schema = UpdateClientDataSchema()
    try:
        validated_data = schema.load(data)
        return validated_data
    except ValidationError as e:
        raise ValueError(f"Validation error: {e.messages}")

def validate_archive_client_data(data):
    """Validate archive client data using marshmallow schema."""
    schema = ArchiveClientDataSchema()
    try:
        validated_data = schema.load(data)
        return validated_data
    except ValidationError as e:
        raise ValueError(f"Validation error: {e.messages}")