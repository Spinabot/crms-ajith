from app.models import Contact
from app.database import db

def test_create_minimal_contact(app):
    with app.app_context():
        contact = Contact(
            jnid="abc123", 
            recid=1, 
            record_type_name="Lead", 
            status_name="New"
        )
        db.session.add(contact)
        db.session.commit()

        retrieved = db.session.get(Contact, "abc123")
        assert retrieved is not None

def test_create_full_contact(app):
    with app.app_context():
        contact = Contact(
            jnid="xyz789",
            first_name="Jane",
            last_name="Doe",
            display_name="Jane D",
            company="Acme Inc.",
            record_type_name="Customer",
            status_name="Active",
            email="jane@example.com",
            mobile_phone="1234567890",
            address_line1="123 Main St",
            city="Springfield",
            state_text="IL",
            zip="62704",
            country_name="USA",
            is_active=True
        )
        db.session.add(contact)
        db.session.commit()

        result = db.session.get(Contact, "xyz789")
        assert result is not None
        assert result.first_name == "Jane"

def test_to_dict_method(app):
    with app.app_context():
        contact = Contact(
            jnid="test456",
            record_type_name="Lead",
            status_name="New",
            first_name="Jane"
        )
        db.session.add(contact)
        db.session.commit()

        result = db.session.get(Contact, "test456")
        d = result.to_dict()
        assert d["jnid"] == "test456"
        assert d["first_name"] == "Jane"
