#!/usr/bin/env python3
"""
Google Cloud Project Setup Script

This script automates the setup of a Google Cloud project for Google Workspace API access.
It uses the Google Cloud API to:
1. Create a new Google Cloud project
2. Enable the necessary APIs
3. Create OAuth 2.0 credentials
4. Download the credentials file

Usage:
    python setup_google_cloud_project.py

Requirements:
    - Python 3.6+
    - google-api-python-client
    - google-auth
    - google-auth-oauthlib
    - google-auth-httplib2

Author: Cline AI
Date: 4/25/2025
"""

import os
import sys
import json
import time
import argparse
from typing import Dict, List, Any, Optional

try:
    from googleapiclient.discovery import build
    from google.oauth2 import service_account
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from google.auth.exceptions import RefreshError
    from googleapiclient.errors import HttpError
except ImportError:
    print("Required packages not installed. Installing...")
    os.system("pip install --upgrade google-api-python-client google-auth google-auth-oauthlib google-auth-httplib2")
    from googleapiclient.discovery import build
    from google.oauth2 import service_account
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from google.auth.exceptions import RefreshError
    from googleapiclient.errors import HttpError

# Configuration
CONFIG = {
    "project_name": "adaptdev-workspace-setup",
    "project_id": "adaptdev-workspace-setup-" + str(int(time.time())),
    "apis_to_enable": [
        "admin.googleapis.com",
        "reseller.googleapis.com",
        "siteverification.googleapis.com",
        "licensing.googleapis.com",
        "cloudresourcemanager.googleapis.com"
    ],
    "oauth_app_name": "AdaptDev Workspace Setup",
    "oauth_support_email": "chase@adaptdev.ai",
    "oauth_scopes": [
        "https://www.googleapis.com/auth/admin.directory.user",
        "https://www.googleapis.com/auth/admin.directory.domain",
        "https://www.googleapis.com/auth/admin.directory.customer",
        "https://www.googleapis.com/auth/apps.order",
        "https://www.googleapis.com/auth/apps.licensing"
    ]
}

# OAuth 2.0 Scopes for this script
SCOPES = [
    'https://www.googleapis.com/auth/cloud-platform'
]

def get_credentials():
    """Get valid user credentials from storage or user input."""
    creds = None
    token_path = 'cloud_token.json'
    
    # Check if token.json exists
    if os.path.exists(token_path):
        print(f"Using existing credentials from {token_path}")
        with open(token_path, 'r') as token:
            creds_data = json.load(token)
            # TODO: Load credentials from token
    else:
        print("No credentials found. Please authenticate with your Google account.")
        flow = InstalledAppFlow.from_client_secrets_file('client_secrets.json', SCOPES)
        creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
    
    return creds

def create_google_cloud_project(creds):
    """Create a new Google Cloud project."""
    try:
        # Build the service
        cloudresourcemanager_service = build('cloudresourcemanager', 'v1', credentials=creds)
        
        # Create a new project
        project = {
            'name': CONFIG['project_name'],
            'projectId': CONFIG['project_id']
        }
        
        operation = cloudresourcemanager_service.projects().create(body=project).execute()
        
        print(f"Google Cloud project creation initiated: {operation}")
        print(f"Project ID: {CONFIG['project_id']}")
        
        # Wait for the project to be created
        print("Waiting for project creation to complete...")
        time.sleep(30)  # Wait for 30 seconds
        
        return CONFIG['project_id']
    except HttpError as e:
        print(f"Error creating Google Cloud project: {e}")
        sys.exit(1)

def enable_apis(creds, project_id):
    """Enable the necessary APIs for the project."""
    try:
        # Build the service
        servicemanagement_service = build('servicemanagement', 'v1', credentials=creds)
        
        for api in CONFIG['apis_to_enable']:
            print(f"Enabling API: {api}")
            operation = servicemanagement_service.services().enable(
                name=f"services/{api}",
                body={"consumerId": f"project:{project_id}"}
            ).execute()
            
            print(f"API enablement initiated: {operation}")
            time.sleep(5)  # Wait for 5 seconds between API enablement
        
        print("All APIs enabled successfully!")
        return True
    except HttpError as e:
        print(f"Error enabling APIs: {e}")
        return False

def create_oauth_credentials(creds, project_id):
    """Create OAuth 2.0 credentials for the project."""
    try:
        # Build the service
        oauth2_service = build('oauth2', 'v2', credentials=creds)
        
        # Create OAuth client
        client = {
            "name": CONFIG['oauth_app_name'],
            "supportEmail": CONFIG['oauth_support_email'],
            "redirectUris": ["http://localhost:8080/"],
            "scopes": CONFIG['oauth_scopes']
        }
        
        result = oauth2_service.clients().insert(
            body=client
        ).execute()
        
        print(f"OAuth 2.0 credentials created: {result}")
        
        # Save credentials to file
        credentials = {
            "installed": {
                "client_id": result['clientId'],
                "client_secret": result['clientSecret'],
                "redirect_uris": ["http://localhost:8080/"],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token"
            }
        }
        
        with open('credentials.json', 'w') as f:
            json.dump(credentials, f)
        
        print("Credentials saved to credentials.json")
        return credentials
    except HttpError as e:
        print(f"Error creating OAuth credentials: {e}")
        return None

def main():
    """Main function to set up Google Cloud project."""
    parser = argparse.ArgumentParser(description='Set up Google Cloud project for Google Workspace API access')
    parser.add_argument('--create-project', action='store_true', help='Create Google Cloud project')
    parser.add_argument('--enable-apis', action='store_true', help='Enable necessary APIs')
    parser.add_argument('--create-credentials', action='store_true', help='Create OAuth 2.0 credentials')
    parser.add_argument('--all', action='store_true', help='Run all steps')
    
    args = parser.parse_args()
    
    # If no arguments provided, show help
    if not any(vars(args).values()):
        parser.print_help()
        return
    
    # Get credentials
    creds = get_credentials()
    
    # Run selected steps
    project_id = CONFIG['project_id']
    
    if args.all or args.create_project:
        project_id = create_google_cloud_project(creds)
    
    if args.all or args.enable_apis:
        enable_apis(creds, project_id)
    
    if args.all or args.create_credentials:
        create_oauth_credentials(creds, project_id)
    
    print("Google Cloud project setup completed successfully!")
    print(f"Project ID: {project_id}")
    print("You can now use the credentials.json file with the setup_google_workspace.py script")

if __name__ == '__main__':
    main()
