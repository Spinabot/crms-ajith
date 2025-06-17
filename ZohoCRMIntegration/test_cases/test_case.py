import json
import requests

# Base URL for the API endpoint
BASE_URL = "http://localhost:5000/api/clients/1/leads"

# List to store IDs of created leads for further operations
created_ids = []

def test_0_read_data():
    """
    Test to read all leads for a specific client.
    - Sends a GET request to fetch all leads.
    - Verifies the response status and structure.
    """
    url = "http://localhost:5000/api/clients/1/leads"
    response = requests.get(url)

    # Check if the status is OK (200)
    assert response.status_code == 200

    # Check if 'data' is present in the response JSON
    json_data = response.json()
    assert "data" in json_data

    # Optionally check if 'data' is a list or has expected keys
    assert isinstance(json_data["data"], list)

def test_1_create_lead():
    """
    Test to create new leads.
    - Reads sample data from a JSON file.
    - Sends a POST request to create leads.
    - Verifies the response status and saves the created lead IDs.
    """
    with open("test_cases/data/sample_data.json") as f:
        payload = json.load(f)

    # Send POST request to create leads
    response = requests.post(BASE_URL, json=payload)
    assert response.status_code == 201  # Check if the resource was created

    response_data = response.json()
    assert "data" in response_data

    # Save created IDs for further tests
    for record in response_data["data"]:
        assert record["code"] == "SUCCESS"  # Ensure the creation was successful
        created_ids.append(record["details"]["id"])  # Store the created lead ID

    # Ensure the number of created IDs matches the input data
    assert len(created_ids) == len(payload["data"])

def test_2_update_lead():
    """
    Test to update existing leads.
    - Reads updated data from a JSON file.
    - Sends a PUT request to update leads using their IDs.
    - Verifies the response status and checks if the updates were successful.
    """
    with open("test_cases/data/updated_data.json") as f:
        updated_payload = json.load(f)

    # Ensure the number of records to update matches the created IDs
    assert len(updated_payload["data"]) == len(created_ids), "Number of records to update must match created IDs"

    # Prepare query parameters with the created IDs (comma-separated)
    params = {"client_id": ",".join(created_ids)}

    # Send PUT request to update leads
    response = requests.put(BASE_URL, json=updated_payload, params=params)
    assert response.status_code == 200  # Check if the update was successful

    response_data = response.json()
    assert "data" in response_data

    # Verify each record in the response
    for record in response_data["data"]:
        assert record["code"] == "SUCCESS"  # Ensure the update was successful
        assert record["message"] == "record updated"  # Check the success message
        assert record["status"] == "success"  # Ensure the status is 'success'

def test_3_delete_lead():
    """
    Test to delete existing leads.
    - Sends a DELETE request with the IDs of the created leads.
    - Verifies the response status and checks if the deletion was successful.
    """
    # Prepare the DELETE URL with the created IDs (comma-separated)
    ids_str = ",".join(created_ids)
    delete_url = f"{BASE_URL}?ids={ids_str}"

    # Send DELETE request to remove leads
    response = requests.delete(delete_url)
    assert response.status_code == 200  # Check if the deletion was successful

    response_data = response.json()
    assert response_data["status"] == "success"  # Ensure the overall status is 'success'

    # Verify each record in the response
    for record in response_data["response"]["data"]:
        assert record["code"] == "SUCCESS"  # Ensure the deletion was successful
        assert record["message"] == "record deleted"  # Check the success message
        assert record["status"] == "success"  # Ensure the status is 'success'
