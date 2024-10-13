import pytest
import json
import requests

# Define the base URL for your AWS-hosted app
BASE_URL = "http://174.129.115.81:5001"

def test_status_endpoint():
    """Test the /status endpoint to check server status."""
    response = requests.get(f"{BASE_URL}/status")
    assert response.status_code == 200
    assert response.json() == {"status": "Server is running"}

def test_predict_endpoint_with_valid_data():
    """Test the /predict endpoint with valid input data."""
    input_data = {
        "input": [0.5] * 33,  # Example 33 feature input data
        "filename": "test_file.csv"
    }
    response = requests.post(
        f"{BASE_URL}/predict",
        data=json.dumps(input_data),
        headers={"Content-Type": "application/json"}
    )

    assert response.status_code == 200
    response_data = response.json()
    assert 'predicted_class' in response_data
    assert 'class_label' in response_data

def test_predict_endpoint_with_invalid_data():
    """Test the /predict endpoint with missing or invalid input data."""
    response = requests.post(
        f"{BASE_URL}/predict",
        data=json.dumps({"input": [0.5] * 32}),  # Invalid: only 32 features
        headers={"Content-Type": "application/json"}
    )

    assert response.status_code == 400
    assert 'error' in response.json()

def test_get_all_records():
    """Test the /records endpoint to fetch all records."""
    response = requests.get(f"{BASE_URL}/records")
    assert response.status_code == 200
    records = response.json()
    assert isinstance(records, list)  # Should return a list of records

def test_get_last_x_records():
    """Test the /records/last/<x> endpoint to fetch the last X records."""
    response = requests.get(f"{BASE_URL}/records/last/2")
    assert response.status_code == 200
    records = response.json()
    assert isinstance(records, list)  # Should return a list of records
    assert len(records) <= 2  # Should return at most 2 records
