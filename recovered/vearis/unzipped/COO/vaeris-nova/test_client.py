#!/usr/bin/env python3
"""
Test client for Vaeris Nova API
"""

import requests
import json
import sys

def test_health():
    """Test the health check endpoint."""
    response = requests.get('http://localhost:5000/api/health')
    print("Health check response:", response.json())
    return response.json()

def test_models():
    """Test the models endpoint."""
    response = requests.get('http://localhost:5000/api/models')
    print("Models response:", json.dumps(response.json(), indent=2))
    return response.json()

def main():
    """Main entry point for the test client."""
    print("Testing Vaeris Nova API...")
    
    try:
        # Test health check
        health = test_health()
        if health.get('status') != 'ok':
            print("Health check failed!")
            return 1
        
        # Test models endpoint
        models = test_models()
        if not models:
            print("Models endpoint returned no data!")
            return 1
        
        print("\nAll tests passed!")
        return 0
        
    except Exception as e:
        print(f"Error testing API: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())