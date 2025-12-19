# Google Workspace Setup for adaptdev.ai

This directory contains scripts and instructions for setting up Google Workspace Business Standard for the adaptdev.ai domain. This setup is part of the Private Mode GCP Setup Blueprint.

## Overview

The setup process involves the following steps:

1. Configure DNS settings in Cloudflare for adaptdev.ai
2. Set up a Google Cloud project with the necessary APIs and credentials
3. Create a Google Workspace Business Standard account
4. Set up primary and secondary users
5. Configure email settings

## Prerequisites

- Python 3.6+
- Access to the Cloudflare account for adaptdev.ai
- A Google account for initial authentication
- The following Python packages:
  - google-api-python-client
  - google-auth
  - google-auth-oauthlib
  - google-auth-httplib2

## Files

- `adaptdev_ai_dns_configuration.md`: Current DNS configuration for adaptdev.ai
- `google_workspace_setup_instructions.md`: Detailed manual instructions for setting up Google Workspace
- `setup_google_cloud_project.py`: Script to set up a Google Cloud project with necessary APIs and credentials
- `setup_google_workspace.py`: Script to create a Google Workspace account and set up users

## Setup Instructions

### 1. Review Current DNS Configuration

Review the current DNS configuration for adaptdev.ai in `adaptdev_ai_dns_configuration.md`. This will help you understand the current state of the domain and what changes need to be made.

### 2. Set Up Google Cloud Project

Run the following command to set up a Google Cloud project with the necessary APIs and credentials:

```bash
python setup_google_cloud_project.py --all
```

This will:
- Create a new Google Cloud project
- Enable the necessary APIs
- Create OAuth 2.0 credentials
- Save the credentials to `credentials.json`

### 3. Set Up Google Workspace

Run the following command to set up Google Workspace for adaptdev.ai:

```bash
python setup_google_workspace.py --all
```

This will:
- Create a Google Workspace Business Standard account
- Set up the primary admin user (chase@adaptdev.ai)
- Set up the secondary user (nova@adaptdev.ai)
- Provide domain verification information

### 4. Verify Domain Ownership

The script will provide a TXT record that needs to be added to the DNS settings in Cloudflare. Follow these steps:

1. Log in to Cloudflare (chase@levelup2x.com)
2. Navigate to the adaptdev.ai domain
3. Go to DNS settings
4. Add the TXT record provided by the script
5. Wait for the DNS changes to propagate (this can take up to 24 hours)

### 5. Configure Email Settings

After the domain is verified, you need to update the MX records to point to Google's mail servers:

1. Log in to Cloudflare
2. Navigate to the adaptdev.ai domain
3. Go to DNS settings
4. Remove the existing MX records
5. Add the following MX records:
   - Priority 1: aspmx.l.google.com
   - Priority 5: alt1.aspmx.l.google.com
   - Priority 5: alt2.aspmx.l.google.com
   - Priority 10: alt3.aspmx.l.google.com
   - Priority 10: alt4.aspmx.l.google.com
6. Update the SPF record:
   - TXT record for adaptdev.ai: "v=spf1 include:_spf.google.com ~all"
7. Set up DKIM through the Google Workspace Admin Console
8. Add a DMARC record:
   - TXT record for _dmarc.adaptdev.ai: "v=DMARC1; p=reject; rua=mailto:chase@adaptdev.ai; ruf=mailto:chase@adaptdev.ai; fo=1"

### 6. Test Email Delivery

After the email settings are configured, test email delivery:

1. Send a test email to chase@adaptdev.ai
2. Send a test email from chase@adaptdev.ai to an external email address
3. Verify that emails are being delivered correctly

## Troubleshooting

### Domain Verification Issues

If you encounter issues with domain verification:

1. Make sure the TXT record is added correctly in Cloudflare
2. Wait for the DNS changes to propagate (this can take up to 24 hours)
3. Check the Google Workspace Admin Console for any error messages

### Email Delivery Issues

If you encounter issues with email delivery:

1. Make sure the MX records are configured correctly
2. Check the SPF, DKIM, and DMARC records
3. Check the Google Workspace Admin Console for any error messages

## Additional Resources

- [Google Workspace Admin Help](https://support.google.com/a/answer/1047213)
- [Cloudflare DNS Documentation](https://developers.cloudflare.com/dns/)
- [Google Workspace API Documentation](https://developers.google.com/admin-sdk)
