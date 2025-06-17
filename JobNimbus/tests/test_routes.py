from unittest.mock import patch
from app.models import Contact
from app.database import db

def test_home(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Welcome to the JobNimbus Contacts API" in response.data

@patch("app.routes.jobnimbus_request")
def test_get_all_contacts(mock_jn, client):
    mock_jn.return_value = ([{"jnid": "123", "first_name": "Test"}], 200)
    response = client.get("/contacts", json={})
    assert response.status_code == 200
    assert response.json == [{"jnid": "123", "first_name": "Test"}]

@patch("app.routes.jobnimbus_request")
def test_create_contact_success(mock_jn, client):
    mock_jn.return_value = ({
        "jnid": "123",
        "first_name": "Test",
        "last_name": "User",
        "display_name": "Test User",
        "company": "SpinAbot",
        "status": 1,
        "status_name": "Active",
        "record_type": 2,
        "record_type_name": "Customer"
    }, 200)

    payload = {
        "first_name": "Test",
        "last_name": "User",
        "display_name": "Test User",
        "company": "SpinAbot",
        "status": 1,
        "status_name": "Active",
        "record_type": 2,
        "record_type_name": "Customer"
    }

    response = client.post("/contacts", json=payload)
    assert response.status_code == 200
    assert "jnid" in response.json

def test_create_contact_missing_body(client):
    response = client.post("/contacts", data="{}", content_type="application/json")
    assert response.status_code == 400
    assert response.json["error"] == "Missing JSON body"

def test_get_contact_success(client):
    contact = Contact(
        jnid="abc123",
        first_name="Test",
        last_name="User",
        record_type_name="Customer",
        status_name="Active"
    )
    db.session.add(contact)
    db.session.commit()

    response = client.get("/contacts/abc123")
    assert response.status_code == 200
    assert response.json["first_name"] == "Test"

def test_get_contact_not_found(client):
    response = client.get("/contacts/doesnotexist")
    assert response.status_code == 404
    assert response.json["error"] == "Contact not found"

@patch("app.routes.jobnimbus_request")
def test_update_contact_success(mock_jn, client):
    contact = Contact(
        jnid="abc123",
        first_name="Old",
        last_name="Name",
        record_type_name="Customer",
        status_name="Active"
    )
    db.session.add(contact)
    db.session.commit()

    mock_jn.return_value = ({"message": "updated"}, 200)
    payload = {"first_name": "New"}
    response = client.put("/contacts/abc123", json=payload)
    assert response.status_code == 200
    assert response.json["message"] == "updated"

def test_update_contact_not_found(client):
    payload = {"first_name": "New"}
    response = client.put("/contacts/invalid123", json=payload)
    assert response.status_code == 404
    assert response.json["error"] == "Contact not found"

@patch("app.routes.jobnimbus_request")
def test_delete_contact_success(mock_jn, client):
    contact = Contact(
        jnid="abc123",
        first_name="Test",
        last_name="User",
        record_type_name="Customer",
        status_name="Active"
    )
    db.session.add(contact)
    db.session.commit()

    mock_jn.return_value = ({"message": "archived"}, 200)
    payload = {"is_active": False}
    response = client.delete("/contacts/abc123", json=payload)
    assert response.status_code == 200
    assert response.json["message"] == "archived"

def test_delete_contact_not_found(client):
    response = client.delete("/contacts/invalid123", json={"is_active": False})
    assert response.status_code == 404
    assert response.json["error"] == "Contact not found"

