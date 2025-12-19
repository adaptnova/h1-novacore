#!/bin/bash
# Script to install and configure mail server software on the ethos server
# Created: 2025-03-28
# Author: Zorion (IBM Cloud Strategist & Provisioning Engineer)

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print section header
print_section() {
    echo -e "\n${YELLOW}===== $1 =====${NC}\n"
}

# Function to print success message
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Function to print error message
print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Function to print info message
print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Check if running as root
if [ "$(id -u)" != "0" ]; then
    print_error "This script must be run as root."
    exit 1
fi

# Domain and server information
DOMAIN="a-d-a-p-t.ai"
MAIL_SUBDOMAIN="mail.$DOMAIN"
SERVER_IP=$(curl -s ifconfig.me)
print_info "Server IP: $SERVER_IP"
print_info "Domain: $DOMAIN"
print_info "Mail subdomain: $MAIL_SUBDOMAIN"

# Update package lists
print_section "Updating package lists"
apt-get update
if [ $? -eq 0 ]; then
    print_success "Package lists updated successfully."
else
    print_error "Failed to update package lists."
    exit 1
fi

# Install required packages
print_section "Installing required packages"
apt-get install -y postfix postfix-mysql dovecot-core dovecot-imapd dovecot-pop3d dovecot-lmtpd dovecot-mysql mysql-server nginx certbot python3-certbot-nginx opendkim opendkim-tools mailutils
if [ $? -eq 0 ]; then
    print_success "Required packages installed successfully."
else
    print_error "Failed to install required packages."
    exit 1
fi

# Configure Postfix
print_section "Configuring Postfix"

# Backup original configuration
cp /etc/postfix/main.cf /etc/postfix/main.cf.bak
print_info "Original Postfix configuration backed up to /etc/postfix/main.cf.bak."

# Create new configuration
cat > /etc/postfix/main.cf << EOF
# See /usr/share/postfix/main.cf.dist for a commented, more complete version

# Debian specific:  Specifying a file name will cause the first
# line of that file to be used as the name.  The Debian default
# is /etc/mailname.
#myorigin = /etc/mailname

smtpd_banner = \$myhostname ESMTP \$mail_name
biff = no

# appending .domain is the MUA's job.
append_dot_mydomain = no

# Uncomment the next line to generate "delayed mail" warnings
#delay_warning_time = 4h

readme_directory = no

# See http://www.postfix.org/COMPATIBILITY_README.html -- default to 2 on
# fresh installs.
compatibility_level = 2

# TLS parameters
smtpd_tls_cert_file=/etc/letsencrypt/live/$MAIL_SUBDOMAIN/fullchain.pem
smtpd_tls_key_file=/etc/letsencrypt/live/$MAIL_SUBDOMAIN/privkey.pem
smtpd_tls_security_level=may
smtpd_tls_loglevel = 1
smtpd_tls_session_cache_database = btree:\${data_directory}/smtpd_scache
smtp_tls_session_cache_database = btree:\${data_directory}/smtp_scache

# See /usr/share/doc/postfix/TLS_README.gz in the postfix-doc package for
# information on enabling SSL in the smtp client.

smtpd_relay_restrictions = permit_mynetworks permit_sasl_authenticated defer_unauth_destination
myhostname = $MAIL_SUBDOMAIN
alias_maps = hash:/etc/aliases
alias_database = hash:/etc/aliases
myorigin = $DOMAIN
mydestination = $MAIL_SUBDOMAIN, $DOMAIN, localhost
relayhost = 
mynetworks = 127.0.0.0/8 [::ffff:127.0.0.0]/104 [::1]/128
mailbox_size_limit = 0
recipient_delimiter = +
inet_interfaces = all
inet_protocols = all

# DKIM
milter_default_action = accept
milter_protocol = 6
smtpd_milters = inet:localhost:12301
non_smtpd_milters = inet:localhost:12301

# Enable SASL authentication
smtpd_sasl_type = dovecot
smtpd_sasl_path = private/auth
smtpd_sasl_auth_enable = yes
smtpd_sasl_security_options = noanonymous
smtpd_sasl_local_domain = $DOMAIN
smtpd_recipient_restrictions = permit_sasl_authenticated,permit_mynetworks,reject_unauth_destination
EOF

if [ $? -eq 0 ]; then
    print_success "Postfix configuration created successfully."
else
    print_error "Failed to create Postfix configuration."
    exit 1
fi

# Configure Dovecot
print_section "Configuring Dovecot"

# Backup original configuration
cp /etc/dovecot/dovecot.conf /etc/dovecot/dovecot.conf.bak
print_info "Original Dovecot configuration backed up to /etc/dovecot/dovecot.conf.bak."

# Create new configuration
cat > /etc/dovecot/dovecot.conf << EOF
# Dovecot configuration for mail server
protocols = imap pop3 lmtp
listen = *

# SSL/TLS configuration
ssl = required
ssl_cert = </etc/letsencrypt/live/$MAIL_SUBDOMAIN/fullchain.pem
ssl_key = </etc/letsencrypt/live/$MAIL_SUBDOMAIN/privkey.pem
ssl_min_protocol = TLSv1.2
ssl_prefer_server_ciphers = yes

# User authentication
auth_mechanisms = plain login
!include conf.d/10-auth.conf

# Mail location
mail_location = maildir:/var/mail/vhosts/%d/%n

# Mailbox configuration
namespace inbox {
  inbox = yes
}

# LMTP configuration
service lmtp {
  unix_listener /var/spool/postfix/private/dovecot-lmtp {
    group = postfix
    mode = 0600
    user = postfix
  }
}

# Authentication for Postfix
service auth {
  unix_listener /var/spool/postfix/private/auth {
    mode = 0666
    user = postfix
    group = postfix
  }
}

# Log configuration
log_path = /var/log/dovecot.log
info_log_path = /var/log/dovecot-info.log
debug_log_path = /var/log/dovecot-debug.log
EOF

if [ $? -eq 0 ]; then
    print_success "Dovecot configuration created successfully."
else
    print_error "Failed to create Dovecot configuration."
    exit 1
fi

# Configure OpenDKIM
print_section "Configuring OpenDKIM"

# Backup original configuration
cp /etc/opendkim.conf /etc/opendkim.conf.bak
print_info "Original OpenDKIM configuration backed up to /etc/opendkim.conf.bak."

# Create new configuration
cat > /etc/opendkim.conf << EOF
# OpenDKIM configuration for mail server
Syslog                  yes
UMask                   002
OversignHeaders         From
TrustAnchorFile         /usr/share/dns/root.key
UserID                  opendkim
Socket                  inet:12301@localhost
PidFile                 /var/run/opendkim/opendkim.pid
SigningTable            refile:/etc/opendkim/signing.table
KeyTable                refile:/etc/opendkim/key.table
ExternalIgnoreList      refile:/etc/opendkim/trusted.hosts
InternalHosts           refile:/etc/opendkim/trusted.hosts
Mode                    sv
Canonicalization        relaxed/simple
SubDomains              no
EOF

if [ $? -eq 0 ]; then
    print_success "OpenDKIM configuration created successfully."
else
    print_error "Failed to create OpenDKIM configuration."
    exit 1
fi

# Create OpenDKIM directories and files
mkdir -p /etc/opendkim/keys/$DOMAIN
chmod -R 700 /etc/opendkim/keys

# Create signing table
echo "*@$DOMAIN mail._domainkey.$DOMAIN" > /etc/opendkim/signing.table

# Create key table
echo "mail._domainkey.$DOMAIN $DOMAIN:mail:/etc/opendkim/keys/$DOMAIN/mail.private" > /etc/opendkim/key.table

# Create trusted hosts
cat > /etc/opendkim/trusted.hosts << EOF
127.0.0.1
localhost
$DOMAIN
$MAIL_SUBDOMAIN
EOF

# Generate DKIM keys
print_info "Generating DKIM keys for $DOMAIN..."
opendkim-genkey -d $DOMAIN -s mail -D /etc/opendkim/keys/$DOMAIN
if [ $? -eq 0 ]; then
    print_success "DKIM keys generated successfully."
else
    print_error "Failed to generate DKIM keys."
    exit 1
fi

# Set permissions
chown -R opendkim:opendkim /etc/opendkim
chmod 640 /etc/opendkim/keys/$DOMAIN/mail.private

# Configure Nginx
print_section "Configuring Nginx"

# Create Nginx configuration for mail subdomain
cat > /etc/nginx/sites-available/$MAIL_SUBDOMAIN << EOF
server {
    listen 80;
    listen [::]:80;
    server_name $MAIL_SUBDOMAIN;

    root /var/www/html;
    index index.html;

    location / {
        try_files \$uri \$uri/ =404;
    }
}
EOF

if [ $? -eq 0 ]; then
    print_success "Nginx configuration created successfully."
else
    print_error "Failed to create Nginx configuration."
    exit 1
fi

# Enable the site
ln -sf /etc/nginx/sites-available/$MAIL_SUBDOMAIN /etc/nginx/sites-enabled/
if [ $? -eq 0 ]; then
    print_success "Nginx site enabled successfully."
else
    print_error "Failed to enable Nginx site."
    exit 1
fi

# Create a simple index.html file
mkdir -p /var/www/html
cat > /var/www/html/index.html << EOF
<!DOCTYPE html>
<html>
<head>
    <title>$MAIL_SUBDOMAIN</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
        h1 {
            color: #333;
        }
        p {
            color: #666;
            line-height: 1.6;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Welcome to $MAIL_SUBDOMAIN</h1>
        <p>This is the mail server for $DOMAIN.</p>
        <p>For more information, please contact the administrator.</p>
    </div>
</body>
</html>
EOF

if [ $? -eq 0 ]; then
    print_success "Index.html file created successfully."
else
    print_error "Failed to create index.html file."
    exit 1
fi

# Test Nginx configuration
nginx -t
if [ $? -eq 0 ]; then
    print_success "Nginx configuration test passed."
else
    print_error "Nginx configuration test failed."
    exit 1
fi

# Restart services
print_section "Restarting services"

# Restart Postfix
systemctl restart postfix
if [ $? -eq 0 ]; then
    print_success "Postfix restarted successfully."
else
    print_error "Failed to restart Postfix."
    exit 1
fi

# Restart Dovecot
systemctl restart dovecot
if [ $? -eq 0 ]; then
    print_success "Dovecot restarted successfully."
else
    print_error "Failed to restart Dovecot."
    exit 1
fi

# Restart OpenDKIM
systemctl restart opendkim
if [ $? -eq 0 ]; then
    print_success "OpenDKIM restarted successfully."
else
    print_error "Failed to restart OpenDKIM."
    exit 1
fi

# Restart Nginx
systemctl restart nginx
if [ $? -eq 0 ]; then
    print_success "Nginx restarted successfully."
else
    print_error "Failed to restart Nginx."
    exit 1
fi

# Enable services to start on boot
print_section "Enabling services to start on boot"

# Enable Postfix
systemctl enable postfix
if [ $? -eq 0 ]; then
    print_success "Postfix enabled to start on boot."
else
    print_error "Failed to enable Postfix to start on boot."
    exit 1
fi

# Enable Dovecot
systemctl enable dovecot
if [ $? -eq 0 ]; then
    print_success "Dovecot enabled to start on boot."
else
    print_error "Failed to enable Dovecot to start on boot."
    exit 1
fi

# Enable OpenDKIM
systemctl enable opendkim
if [ $? -eq 0 ]; then
    print_success "OpenDKIM enabled to start on boot."
else
    print_error "Failed to enable OpenDKIM to start on boot."
    exit 1
fi

# Enable Nginx
systemctl enable nginx
if [ $? -eq 0 ]; then
    print_success "Nginx enabled to start on boot."
else
    print_error "Failed to enable Nginx to start on boot."
    exit 1
fi

# Obtain SSL certificate
print_section "Obtaining SSL certificate"
print_info "This step requires that the DNS A record for $MAIL_SUBDOMAIN is already configured and propagated."
print_info "If you haven't configured the DNS records yet, please run the configure_dns_records.sh script first."
print_info "Do you want to proceed with obtaining the SSL certificate? (y/n)"
read -p "Enter your choice: " choice

if [ "$choice" = "y" ] || [ "$choice" = "Y" ]; then
    certbot --nginx -d $MAIL_SUBDOMAIN --non-interactive --agree-tos --email chase@levelup2x.com
    if [ $? -eq 0 ]; then
        print_success "SSL certificate obtained successfully."
    else
        print_error "Failed to obtain SSL certificate."
        print_info "You can try again later by running: certbot --nginx -d $MAIL_SUBDOMAIN"
    fi
else
    print_info "Skipping SSL certificate obtainment."
    print_info "You can obtain the SSL certificate later by running: certbot --nginx -d $MAIL_SUBDOMAIN"
fi

# Create mail user
print_section "Creating mail user"
print_info "Creating mail user 'admin@$DOMAIN'..."

# Create mail directory
mkdir -p /var/mail/vhosts/$DOMAIN/admin
if [ $? -eq 0 ]; then
    print_success "Mail directory created successfully."
else
    print_error "Failed to create mail directory."
    exit 1
fi

# Set permissions
chown -R vmail:vmail /var/mail/vhosts
chmod -R 770 /var/mail/vhosts

# Set password for admin user
print_info "Setting password for admin@$DOMAIN..."
echo "admin@$DOMAIN:$(openssl passwd -1 'x'):::::::" >> /etc/dovecot/users
if [ $? -eq 0 ]; then
    print_success "Mail user created successfully."
    print_info "Username: admin@$DOMAIN"
    print_info "Password: x"
else
    print_error "Failed to create mail user."
    exit 1
fi

print_section "Summary"
print_success "Mail server software installed and configured successfully."
print_info "The following services have been installed and configured:"
print_info "- Postfix (SMTP server)"
print_info "- Dovecot (IMAP/POP3 server)"
print_info "- OpenDKIM (DKIM signing)"
print_info "- Nginx (Web server)"
print_info "- Certbot (SSL certificate)"

print_section "Next Steps"
print_info "1. Configure DNS records for the mail server using the configure_dns_records.sh script."
print_info "2. Test the mail server functionality."
print_info "3. Configure mail clients to use the mail server."

print_info "Mail server details:"
print_info "- SMTP server: $MAIL_SUBDOMAIN"
print_info "- IMAP server: $MAIL_SUBDOMAIN"
print_info "- POP3 server: $MAIL_SUBDOMAIN"
print_info "- Webmail: Not installed (you can install Roundcube or SquirrelMail if needed)"
print_info "- Test account: admin@$DOMAIN (password: x)"