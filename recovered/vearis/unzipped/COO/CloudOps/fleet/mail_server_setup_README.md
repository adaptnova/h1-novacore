# Mail Server Setup for a-d-a-p-t.ai

This document provides instructions for setting up a mail server on the ethos server for the a-d-a-p-t.ai domain.

## Overview

The mail server setup consists of the following components:

1. **Postfix** - SMTP server for sending and receiving emails
2. **Dovecot** - IMAP/POP3 server for accessing emails
3. **OpenDKIM** - DKIM signing for email authentication
4. **Nginx** - Web server for hosting webmail and Let's Encrypt verification
5. **Certbot** - SSL certificate management

## Prerequisites

- Ethos server with Debian 12.9
- DNS records for mail.a-d-a-p-t.ai pointing to the server's IP address
- Cloudflare API credentials for DNS configuration

## Setup Process

The setup process is divided into the following steps:

1. Open required ports in the security group
2. Configure DNS records
3. Install and configure mail server software
4. Test mail server functionality

## Scripts

The following scripts are provided to automate the setup process:

### 1. open_mail_server_ports_ethos.sh

This script opens the required ports in the security group for the ethos server:

- Port 25 (TCP) - SMTP - Receiving mail from other mail servers
- Port 465 (TCP) - SMTPS - Secure SMTP (legacy)
- Port 587 (TCP) - Submission - Sending mail (with authentication)
- Port 143 (TCP) - IMAP - Mail access (unencrypted)
- Port 993 (TCP) - IMAPS - Secure IMAP mail access
- Port 110 (TCP) - POP3 - Mail access (unencrypted)
- Port 995 (TCP) - POP3S - Secure POP3 mail access
- Port 4190 (TCP) - Sieve - Mail filtering
- Port 80 (TCP) - HTTP - Web access and Let's Encrypt verification
- Port 443 (TCP) - HTTPS - Secure web access

Usage:

```bash
./open_mail_server_ports_ethos.sh
```

### 2. check_mail_ports.sh

This script checks if the required ports are open on the server:

Usage:

```bash
./check_mail_ports.sh
```

### 3. configure_dns_records.sh

This script configures the DNS records for the mail server using the Cloudflare API:

- A record for mail.a-d-a-p-t.ai pointing to the server's IP address
- MX record for a-d-a-p-t.ai pointing to mail.a-d-a-p-t.ai
- SPF record for a-d-a-p-t.ai
- DKIM record for mail._domainkey.a-d-a-p-t.ai
- DMARC record for _dmarc.a-d-a-p-t.ai

Before running this script, you need to create a .env file with your Cloudflare credentials:

```bash
cp .env.cloudflare .env
# Edit .env and add your Cloudflare credentials
```

Usage:

```bash
./configure_dns_records.sh
```

### 4. install_mail_server.sh

This script installs and configures the mail server software:

- Installs Postfix, Dovecot, OpenDKIM, Nginx, and Certbot
- Configures Postfix for SMTP
- Configures Dovecot for IMAP/POP3
- Configures OpenDKIM for DKIM signing
- Configures Nginx for hosting webmail and Let's Encrypt verification
- Obtains SSL certificate from Let's Encrypt
- Creates a test mail user (admin@a-d-a-p-t.ai)

Usage:

```bash
./install_mail_server.sh
```

## Testing

After completing the setup process, you can test the mail server functionality:

1. Send a test email from the server:

```bash
echo "Test email" | mail -s "Test" your-email@example.com
```

2. Configure a mail client to connect to the server:

- SMTP server: mail.a-d-a-p-t.ai
- IMAP server: mail.a-d-a-p-t.ai
- POP3 server: mail.a-d-a-p-t.ai
- Username: admin@a-d-a-p-t.ai
- Password: x

## Troubleshooting

If you encounter any issues, check the following:

1. Security group rules:

```bash
./check_mail_ports.sh
```

2. DNS records:

```bash
dig +short MX a-d-a-p-t.ai
dig +short A mail.a-d-a-p-t.ai
dig +short TXT a-d-a-p-t.ai
dig +short TXT mail._domainkey.a-d-a-p-t.ai
dig +short TXT _dmarc.a-d-a-p-t.ai
```

3. Service status:

```bash
systemctl status postfix
systemctl status dovecot
systemctl status opendkim
systemctl status nginx
```

4. Log files:

```bash
tail -f /var/log/mail.log
tail -f /var/log/dovecot.log
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

## Additional Configuration

### Webmail

You can install a webmail client like Roundcube or SquirrelMail:

```bash
apt-get install -y roundcube roundcube-mysql
```

### Spam Filtering

You can install SpamAssassin for spam filtering:

```bash
apt-get install -y spamassassin spamc
```

### Virus Scanning

You can install ClamAV for virus scanning:

```bash
apt-get install -y clamav clamav-daemon
```

## Maintenance

### SSL Certificate Renewal

Let's Encrypt SSL certificates are valid for 90 days and are automatically renewed by Certbot.

### Backup

You should regularly backup the following:

- Mail data: /var/mail/vhosts
- Configuration files: /etc/postfix, /etc/dovecot, /etc/opendkim, /etc/nginx
- SSL certificates: /etc/letsencrypt

## Security Considerations

- Keep the server updated with security patches
- Use strong passwords for mail users
- Configure firewall rules to restrict access to the server
- Monitor the server for suspicious activity
- Implement SPF, DKIM, and DMARC for email authentication
- Use SSL/TLS for secure communication