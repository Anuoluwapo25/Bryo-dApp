#!/usr/bin/env python
"""
Test script for Privy API integration
Run this script from your project root to test Privy API connectivity
"""

import os
import sys
import requests
import time
import hmac
import hashlib
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Privy API credentials
API_KEY = os.getenv('PRIVY_API_KEY')
API_SECRET = os.getenv('PRIVY_API_SECRET')
BASE_URL = 'https://auth.privy.io/api/v1'

if not API_KEY or not API_SECRET:
    print("Error: PRIVY_API_KEY and PRIVY_API_SECRET must be set in .env file")
    sys.exit(1)

def generate_headers():
    """Generate headers with authentication for Privy API requests"""
    timestamp = str(int(time.time()))
    message = f"{timestamp}:{API_KEY}"
    signature = hmac.new(
        API_SECRET.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    return {
        'Content-Type': 'application/json',
        'X-Privy-API-Key': API_KEY,
        'X-Privy-API-Timestamp': timestamp,
        'X-Privy-API-Signature': signature
    }

def test_create_login_link():
    """Test creating a login link with Privy"""
    endpoint = f"{BASE_URL}/links"
    
    payload = {
        'email': 'test@example.com',
        'redirectUrl': 'http://localhost:3000/callback'
    }
    
    print(f"Sending request to {endpoint}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(
            endpoint,
            headers=generate_headers(),
            json=payload
        )
        
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            print("Success! Response:")
            print(json.dumps(response.json(), indent=2))
            return True
        else:
            print("Error! Response:")
            print(response.text)
            return False
    except Exception as e:
        print(f"Exception occurred: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing Privy API integration...")
    print(f"API Key: {API_KEY[:5]}{'*' * (len(API_KEY) - 5)}")
    
    success = test_create_login_link()
    
    if success:
        print("\n✅ Privy API test passed! Your credentials are working correctly.")
    else:
        print("\n❌ Privy API test failed. Please check your credentials and try again.")