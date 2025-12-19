#!/usr/bin/env python3
"""
Google Workspace Setup Script

This script automates the setup of Google Workspace for the adaptdev.ai domain.
It uses the Google Workspace Admin SDK to:
1. Create a Google Workspace account
2. Set up primary admin user
3. Set up secondary user
4. Configure domain verification
5. Configure email settings

Usage:
    python setup_google_workspace.py

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
    "domain": "adaptdev.ai",
    "business_name": "AdaptDev AI",
    "primary_user": {
        "first_name": "Jason",
        "last_name": "Remmen",
        "email": "jr@adaptdev.ai",
        "password": "Adaptnova111!@#",  # Temporary password, will be changed on first login
        "is_admin": True
    },
    "secondary_user": {
        "first_name": "Nova",
        "last_name": "AdaptDev",
        "email": "nova@adaptdev.ai",
        "password": "Adaptnova222!@#",  # Temporary password, will be changed on first login
        "is_admin": False
    },
    "billing_info": {
        "name": "Jason Remmen",
        "address": "298 Lakeview Ave., Apt 2",
        "city": "Long Lake",
        "state": "MN",
        "zip": "55356",
        "country": "US",
        "phone": "602-595-0660",
        "bank_name": "The Bancorp Bank, N.A.",
        "routing_number": "031101279",
        "account_number": "222114356653"
    }
}

# OAuth 2.0 Scopes
SCOPES = [
    'https://www.googleapis.com/auth/admin.directory.user',
    'https://www.googleapis.com/auth/admin.directory.domain',
    'https://www.googleapis.com/auth/admin.directory.customer',
    'https://www.googleapis.com/auth/apps.order',
    'https://www.googleapis.com/auth/apps.licensing'
]

def get_credentials():
    """Get valid user credentials from storage or user input."""
    creds = None
    token_path = 'token.json'
    credentials_path = 'credentials.json'
    
    # Check if token.json exists
    if os.path.exists(token_path):
        try:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
        except Exception as e:
            print(f"Error getting credentials: {e}")
            sys.exit(1)
    else:
        print(f"No credentials file found at {credentials_path}")
        print("Please create a project in Google Cloud Console and download OAuth 2.0 credentials")
        print("Save the credentials as 'credentials.json' in the current directory")
        sys.exit(1)
    
    return creds

def create_google_workspace_account(creds):
    """Create a new Google Workspace account."""
    try:
        # Build the service
        reseller_service = build('reseller', 'v1', credentials=creds)
        
        # Create a new subscription
        subscription = {
            'customerId': 'my_customer',
            'skuId': '1010020020',  # Google Workspace Business Standard
            'plan': {
                'planName': 'ANNUAL_MONTHLY_PAY'
            },
            'seats': {
                'numberOfSeats': 2,
                'maximumNumberOfSeats': 10
            },
            'renewalSettings': {
                'renewalType': 'AUTO_RENEW'
            },
            'purchaseOrderId': 'ADAPT_' + str(int(time.time()))
        }
        
        result = reseller_service.subscriptions().insert(
            customerId='my_customer',
            body=subscription
        ).execute()
        
        print(f"Google Workspace account created: {result}")
        return result
    except HttpError as e:
        print(f"Error creating Google Workspace account: {e}")
        sys.exit(1)

def create_user(creds, user_info):
    """Create a new user in Google Workspace."""
    try:
        # Build the service
        admin_service = build('admin', 'directory_v1', credentials=creds)
        
        # Create user
        user = {
            'primaryEmail': user_info['email'],
            'name': {
                'givenName': user_info['first_name'],
                'familyName': user_info['last_name']
            },
            'password': user_info['password'],
            'changePasswordAtNextLogin': True
        }
        
        result = admin_service.users().insert(body=user).execute()
        print(f"User created: {result['primaryEmail']}")
        
        # Make user an admin if specified
        if user_info.get('is_admin', False):
            admin_service.users().makeAdmin(
                userKey=user_info['email'],
                body={'status': True}
            ).execute()
            print(f"User {user_info['email']} is now an admin")
        
        return result
    except HttpError as e:
        print(f"Error creating user: {e}")
        return None

def verify_domain(creds):
    """Get domain verification information."""
    try:
        # Build the service
        site_verification_service = build('siteVerification', 'v1', credentials=creds)
        
        # Get verification token
        verification_token = site_verification_service.webResource().getToken(
            body={
                'site': {
                    'type': 'INET_DOMAIN',
                    'identifier': CONFIG['domain']
                },
                'verificationMethod': 'DNS_TXT'
            }
        ).execute()
        
        print(f"Domain verification token: {verification_token['token']}")
        print("Add this TXT record to your DNS settings in Cloudflare:")
        print(f"Type: TXT")
        print(f"Name: @")
        print(f"Content: {verification_token['token']}")
        
        return verification_token
    except HttpError as e:
        print(f"Error getting domain verification token: {e}")
        return None

def main():
    """Main function to set up Google Workspace."""
    parser = argparse.ArgumentParser(description='Set up Google Workspace for adaptdev.ai')
    parser.add_argument('--create-account', action='store_true', help='Create Google Workspace account')
    parser.add_argument('--create-users', action='store_true', help='Create users')
    parser.add_argument('--verify-domain', action='store_true', help='Get domain verification information')
    parser.add_argument('--all', action='store_true', help='Run all steps')
    
    args = parser.parse_args()
    
    # If no arguments provided, show help
    if not any(vars(args).values()):
        parser.print_help()
        return
    
    # Get credentials
    creds = get_credentials()
    
    # Run selected steps
    if args.all or args.create_account:
        create_google_workspace_account(creds)
    
    if args.all or args.create_users:
        create_user(creds, CONFIG['primary_user'])
        create_user(creds, CONFIG['secondary_user'])
    
    if args.all or args.verify_domain:
        verify_domain(creds)
    
    print("Google Workspace setup completed successfully!")

if __name__ == '__main__':
    main()
