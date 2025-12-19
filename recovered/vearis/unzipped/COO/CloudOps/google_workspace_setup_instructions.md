# Google Workspace Setup Instructions

## Overview
This document provides step-by-step instructions for setting up Google Workspace Business Standard for the adaptdev.ai domain. These instructions are part of the Private Mode GCP Setup Blueprint.

## Prerequisites
- Access to the Cloudflare account for adaptdev.ai
- Personal information for the primary admin account
- Bank account information for billing

## Account Information
- **Business Name**: AdaptDev AI
- **Number of Employees**: 2-9
- **Primary Admin**: Jason Remmen
  - **Email**: chase@adaptdev.ai
  - **Address**: 298 Lakeview Ave., Apt 2, Long Lake, MN 55356
  - **Phone Number**: 602-595-0660
  - **Recovery Email**: jr@a-d-a-p-t.com
- **Secondary User**: Nova
  - **Email**: nova@adaptdev.ai
- **Billing Information**:
  - **Bank**: The Bancorp Bank, N.A.
  - **Routing Number**: 031101279
  - **Account Number**: 222114356653

## Setup Steps

### 1. Sign Up for Google Workspace Business Standard
1. Go to https://workspace.google.com/business/signup/welcome
2. Enter "AdaptDev AI" as the business name
3. Select "2-9" for the number of employees
4. Select "United States" as the region
5. Enter your name and contact information
6. Enter "adaptdev.ai" as your domain
7. Confirm that you own the domain
8. Create the primary admin account (chase@adaptdev.ai)
9. Enter the billing information
10. Accept the terms and conditions

### 2. Verify Domain Ownership
1. Google will provide a TXT record to add to your DNS settings in Cloudflare
2. Log in to Cloudflare (chase@levelup2x.com)
3. Navigate to the adaptdev.ai domain
4. Go to DNS settings
5. Add the TXT record provided by Google
6. Return to Google Workspace setup and verify the domain

### 3. Configure MX Records
1. In Cloudflare, update the MX records to point to Google's mail servers:
   - Priority 1: aspmx.l.google.com
   - Priority 5: alt1.aspmx.l.google.com
   - Priority 5: alt2.aspmx.l.google.com
   - Priority 10: alt3.aspmx.l.google.com
   - Priority 10: alt4.aspmx.l.google.com
2. Remove the existing Cloudflare MX records

### 4. Configure SPF, DKIM, and DMARC Records
1. Update the SPF record:
   - TXT record for adaptdev.ai: "v=spf1 include:_spf.google.com ~all"
2. Set up DKIM:
   - Follow Google's instructions to generate a DKIM key
   - Add the DKIM record to Cloudflare DNS
3. Update the DMARC record:
   - TXT record for _dmarc.adaptdev.ai: "v=DMARC1; p=reject; rua=mailto:chase@adaptdev.ai; ruf=mailto:chase@adaptdev.ai; fo=1"

### 5. Set Up Secondary User
1. Log in to the Google Admin Console
2. Navigate to Users
3. Add a new user with the following information:
   - First Name: Nova
   - Last Name: AdaptDev
   - Email: nova@adaptdev.ai
4. Set a temporary password and require password change on first login

### 6. Test Email Delivery
1. Send a test email to chase@adaptdev.ai
2. Send a test email from chase@adaptdev.ai to an external email address
3. Verify that emails are being delivered correctly

## Notes
- The domain adaptdev.ai is currently using Cloudflare's email routing service
- The MX records will need to be updated to point to Google's mail servers
- The SPF, DKIM, and DMARC records will need to be updated for Google Workspace
- The domain verification process may take up to 24 hours to complete
