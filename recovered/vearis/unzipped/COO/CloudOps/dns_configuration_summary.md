# a-d-a-p-t.ai DNS Configuration Summary

## Overview
This document summarizes the current DNS configuration for the a-d-a-p-t.ai domain in Cloudflare. This information will be used as reference for the Google Workspace setup.

## DNS Records

### A Records
- a-d-a-p-t.ai → 103.169.142.0
- code.a-d-a-p-t.ai → 34.133.22.192
- gui.a-d-a-p-t.ai → 76.76.21.21
- mail.a-d-a-p-t.ai → 52.118.187.172
- www.a-d-a-p-t.ai → 103.169.142.0

### MX Records
- a-d-a-p-t.ai → route1.mx.cloudflare.net (priority 20)
- a-d-a-p-t.ai → route2.mx.cloudflare.net (priority 7)
- a-d-a-p-t.ai → route3.mx.cloudflare.net (priority 38)
- mail.a-d-a-p-t.ai → route1.mx.cloudflare.net (priority 20)
- mail.a-d-a-p-t.ai → route2.mx.cloudflare.net (priority 7)
- mail.a-d-a-p-t.ai → route3.mx.cloudflare.net (priority 38)

### TXT Records
- a-d-a-p-t.ai → "v=spf1 include:_spf.mx.cloudflare.net ~all" (SPF record)
- _dmarc.a-d-a-p-t.ai → "v=DMARC1; p=reject; ..." (DMARC record)
- mail._domainkey.a-d-a-p-t.ai → "v=DKIM1; h=sha256; k=rsa; p=..." (DKIM record)
- *._domainkey.a-d-a-p-t.ai → "v=DKIM1; p=" (DKIM record)
- mail.a-d-a-p-t.ai → "v=spf1 include:_spf.mx.cloudflare.net ~all" (SPF record)

### NS Records
- a-d-a-p-t.ai → cosmin.ns.cloudflare.com
- a-d-a-p-t.ai → elly.ns.cloudflare.com

## Google Workspace Verification
For Google Workspace verification, we will need to add a specific TXT record or CNAME record as specified by Google during the verification process. This will be done in Task 2.2: Google Workspace Account Creation.

## Email Configuration
The domain is currently configured to use Cloudflare's email routing service with proper SPF, DKIM, and DMARC records for email authentication and security. When setting up Google Workspace, we will need to update the MX records to point to Google's mail servers.

## Next Steps
1. Sign up for Google Workspace Business Standard free trial
2. Create primary admin account: jason@a-d-a-p-t.ai
3. Add Google Workspace verification record to DNS
4. Update MX records to point to Google's mail servers
5. Test email delivery
