from datetime import datetime
from typing import Dict, List, Optional
from marshmallow import Schema, fields, ValidationError, validates_schema

# Base schema class for validation
class BaseSchema(Schema):
    pass

class ClientSchema(BaseSchema):
    access_token = fields.Str(required=True)
    refresh_token = fields.Str(required=True)
    extracted_time = fields.DateTime(required=True)

class EmailSchema(BaseSchema):
    address = fields.Str(required=True)
    primary = fields.Bool(allow_none=True)

class PhoneSchema(BaseSchema):
    number = fields.Str(required=True)
    primary = fields.Bool(allow_none=True)

class BillingAddressSchema(BaseSchema):
    street1 = fields.Str(allow_none=True)
    street2 = fields.Str(allow_none=True)
    city = fields.Str(allow_none=True)
    province = fields.Str(allow_none=True)
    country = fields.Str(allow_none=True)
    postalCode = fields.Str(allow_none=True)

class PropertyAddressSchema(BaseSchema):
    street1 = fields.Str(allow_none=True)
    street2 = fields.Str(allow_none=True)
    city = fields.Str(allow_none=True)
    province = fields.Str(allow_none=True)
    country = fields.Str(allow_none=True)
    postalCode = fields.Str(allow_none=True)

class ClientCreateDataSchema(BaseSchema):
    firstName = fields.Str(allow_none=True)
    lastName = fields.Str(allow_none=True)
    companyName = fields.Str(allow_none=True)
    emails = fields.List(fields.Nested(EmailSchema), allow_none=True)
    phones = fields.List(fields.Nested(PhoneSchema), allow_none=True)
    billingAddress = fields.Nested(BillingAddressSchema, allow_none=True)

    @validates_schema
    def validate_required_fields(self, data, **kwargs):
        """Ensure at least firstName or lastName or companyName is provided."""
        if not data.get('firstName') and not data.get('lastName') and not data.get('companyName'):
            raise ValidationError("At least one of firstName, lastName, or companyName must be provided")

class UpdateClientDataSchema(BaseSchema):
    clientId = fields.Str(required=True)
    firstName = fields.Str(allow_none=True)
    lastName = fields.Str(allow_none=True)
    companyName = fields.Str(allow_none=True)
    emailsToAdd = fields.List(fields.Nested(EmailSchema), allow_none=True)
    phonesToAdd = fields.List(fields.Nested(PhoneSchema), allow_none=True)
    propertyAddressesToAdd = fields.List(fields.Nested(PropertyAddressSchema), allow_none=True)
    emailsToDelete = fields.List(fields.Str(), allow_none=True)
    phonesToDelete = fields.List(fields.Str(), allow_none=True)
    propertyAddressesToDelete = fields.List(fields.Str(), allow_none=True)

    @validates_schema
    def validate_deletions(self, data, **kwargs):
        # These checks should be performed in the route with current state, but we add a placeholder here
        pass

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