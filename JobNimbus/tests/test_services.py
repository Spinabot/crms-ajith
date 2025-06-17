import pytest
from unittest.mock import patch, MagicMock
from app import services

# Patch current_app.config to mock the API key
@pytest.fixture(autouse=True)
def mock_current_app(monkeypatch):
    class MockApp:
        config = {"JOBNIMBUS_API_KEY": "fake_api_key"}
    monkeypatch.setattr("app.services.current_app", MockApp())

@patch("app.services.requests.post")
def test_create_contact_in_jobnimbus(mock_post):
    mock_response = MagicMock()
    mock_response.json.return_value = {"jnid": "123", "first_name": "John"}
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    payload = {"first_name": "John", "last_name": "Doe"}
    result = services.create_contact_in_jobnimbus(payload)

    mock_post.assert_called_once()
    assert result["jnid"] == "123"
    assert result["first_name"] == "John"

@patch("app.services.requests.get")
def test_get_contact_from_jobnimbus(mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = {"jnid": "123", "first_name": "Jane"}
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    contact_id = "123"
    result = services.get_contact_from_jobnimbus(contact_id)

    mock_get.assert_called_once_with(f"https://app.jobnimbus.com/api1/{contact_id}", headers=services.get_headers())
    assert result["jnid"] == "123"
    assert result["first_name"] == "Jane"

@patch("app.services.requests.put")
def test_update_contact_in_jobnimbus(mock_put):
    mock_response = MagicMock()
    mock_response.json.return_value = {"jnid": "123", "first_name": "Updated"}
    mock_response.raise_for_status.return_value = None
    mock_put.return_value = mock_response

    contact_id = "123"
    payload = {"first_name": "Updated"}
    result = services.update_contact_in_jobnimbus(contact_id, payload)

    mock_put.assert_called_once_with(
        f"https://app.jobnimbus.com/api1/{contact_id}",
        headers=services.get_headers(),
        json=payload
    )
    assert result["first_name"] == "Updated"

@patch("app.services.requests.delete")
def test_delete_contact_in_jobnimbus(mock_delete):
    mock_response = MagicMock()
    mock_response.status_code = 204
    mock_response.raise_for_status.return_value = None
    mock_delete.return_value = mock_response

    contact_id = "123"
    result = services.delete_contact_in_jobnimbus(contact_id)

    mock_delete.assert_called_once_with(
        f"https://app.jobnimbus.com/api1/{contact_id}",
        headers=services.get_headers()
    )
    assert result is True
