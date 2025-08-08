#!/usr/bin/env python3
"""
Simple script to test the GA4 MCP Chat backend directly
"""

import argparse
import json
import os
import requests
from pathlib import Path

def load_env():
    """Load environment variables from .env file"""
    env_file = Path(".env")
    
    if env_file.exists():
        with open(env_file, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                key, value = line.split("=", 1)
                os.environ[key] = value

def test_local_query(query, password=None, url=None):
    """Test a query against the local or remote backend"""
    if not password:
        # Try to get password from environment
        load_env()
        password = os.environ.get("CHAT_PASSWORD", "changeme")
    
    if not url:
        url = "http://localhost:8000/query"
    
    print(f"\nSending query to {url}:\n\"{query}\"\n")
    
    try:
        response = requests.post(
            url,
            json={"password": password, "message": query},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print("Response:\n")
            print(data["reply"])
            return True
        elif response.status_code == 401:
            print("Error: Authentication failed. Check your password.")
            return False
        else:
            print(f"Error: Received status code {response.status_code}")
            print(response.text)
            return False
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the backend server.")
        print("Make sure the server is running and the URL is correct.")
        return False
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Test the GA4 MCP Chat backend")
    parser.add_argument("query", help="The query to send to the backend")
    parser.add_argument("--password", "-p", help="The password to use for authentication")
    parser.add_argument("--url", "-u", help="The URL of the backend API")
    
    args = parser.parse_args()
    
    test_local_query(args.query, args.password, args.url)

if __name__ == "__main__":
    main()