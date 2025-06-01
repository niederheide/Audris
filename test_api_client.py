"""
Test client for the Audris API.

This script provides utility functions to test the Audris API
by generating test tokens and making API requests.
"""
import requests
import jwt
import json
import base64
import argparse
from datetime import datetime, timedelta

# API configuration
API_URL = "http://localhost:8000"  # Update with the actual API URL
SECRET_KEY = "syntechai_super_secret_key"
ALGORITHM = "HS256"

def create_test_token(client_id="test_client", expiry_minutes=60):
    """
    Create a test JWT token.
    
    Args:
        client_id: Client identifier
        expiry_minutes: Token expiry time in minutes
        
    Returns:
        JWT token string
    """
    expiry = datetime.utcnow() + timedelta(minutes=expiry_minutes)
    payload = {
        "client_id": client_id,
        "exp": expiry
    }
    
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

def make_api_request(endpoint, method="GET", data=None, token=None):
    """
    Make a request to the Audris API.
    
    Args:
        endpoint: API endpoint
        method: HTTP method
        data: Request data
        token: JWT token
        
    Returns:
        API response
    """
    url = f"{API_URL}{endpoint}"
    headers = {}
    
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    if method == "GET":
        response = requests.get(url, headers=headers)
    elif method == "POST":
        headers["Content-Type"] = "application/json"
        response = requests.post(url, json=data, headers=headers)
    else:
        raise ValueError(f"Unsupported method: {method}")
    
    return response

def test_health_check():
    """Test the health check endpoint."""
    print("\n=== Testing Health Check Endpoint ===")
    response = make_api_request("/health")
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.json()}")

def test_protected_endpoint(token=None):
    """Test a protected endpoint."""
    if not token:
        token = create_test_token()
        
    print("\n=== Testing Protected Endpoint ===")
    print(f"Using token: {token}")
    
    # Test the alerts endpoint
    response = make_api_request("/alerts", token=token)
    print(f"Status code: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {response.json()}")
    else:
        print(f"Error: {response.text}")

def main():
    """Run the API tests."""
    parser = argparse.ArgumentParser(description="Test the Audris API")
    parser.add_argument("--token", help="Use an existing JWT token")
    parser.add_argument("--generate-token", action="store_true", help="Generate a new JWT token")
    parser.add_argument("--client-id", default="test_client", help="Client ID for token generation")
    
    args = parser.parse_args()
    
    # Generate token if requested
    if args.generate_token:
        token = create_test_token(client_id=args.client_id)
        print(f"Generated token: {token}")
        return
    
    # Use provided token or generate a new one
    token = args.token or create_test_token()
    
    # Run tests
    test_health_check()
    test_protected_endpoint(token)

if __name__ == "__main__":
    main()