#!/bin/bash
# Script to configure mail services to listen on all required ports
# Created: 2025-03-29
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

# Configure Postfix to listen on ports 465 and 587
print_section "Configuring Postfix to listen on ports 465 and 587"

# Backup original configuration
cp /etc/postfix/master.cf /etc/postfix/master.cf.bak
print_info "Original Postfix configuration backed up to /etc/postfix/master.cf.bak."

# Configure Postfix to listen on port 465 (SMTPS)
print_info "Configuring Postfix to listen on port 465 (SMTPS)..."
if grep -q "^smtps" /etc/postfix/master.cf; then
    print_info "Postfix is already configured to listen on port 465."
else
    cat >> /etc/postfix/master.cf << EOF
smtps     inet  n       -       y       -       -       smtpd
  -o syslog_name=postfix/smtps
  -o smtpd_tls_wrappermode=yes
  -o smtpd_sasl_auth_enable=yes
  -o smtpd_client_restrictions=permit_sasl_authenticated,reject
EOF
    print_success "Postfix configured to listen on port 465."
fi

# Configure Postfix to listen on port 587 (Submission)
print_info "Configuring Postfix to listen on port 587 (Submission)..."
if grep -q "^submission" /etc/postfix/master.cf; then
    print_info "Postfix is already configured to listen on port 587."
else
    cat >> /etc/postfix/master.cf << EOF
submission inet n       -       y       -       -       smtpd
  -o syslog_name=postfix/submission
  -o smtpd_tls_security_level=encrypt
  -o smtpd_sasl_auth_enable=yes
  -o smtpd_client_restrictions=permit_sasl_authenticated,reject
EOF
    print_success "Postfix configured to listen on port 587."
fi

# Restart Postfix
print_info "Restarting Postfix..."
systemctl restart postfix
if [ $? -eq 0 ]; then
    print_success "Postfix restarted successfully."
else
    print_error "Failed to restart Postfix."
    exit 1
fi

# Configure Dovecot to listen on port 4190 (Sieve)
print_section "Configuring Dovecot to listen on port 4190 (Sieve)"

# Backup original configuration
cp /etc/dovecot/conf.d/20-managesieve.conf /etc/dovecot/conf.d/20-managesieve.conf.bak 2>/dev/null
print_info "Original Dovecot ManageSieve configuration backed up (if it exists)."

# Create ManageSieve configuration
print_info "Creating ManageSieve configuration..."
cat > /etc/dovecot/conf.d/20-managesieve.conf << EOF
##
## ManageSieve specific settings
##

# Uncomment to enable managesieve protocol:
protocols = \$protocols sieve

service managesieve-login {
  inet_listener sieve {
    port = 4190
  }
}

service managesieve {
}

protocol sieve {
}
EOF
print_success "ManageSieve configuration created."

# Restart Dovecot
print_info "Restarting Dovecot..."
systemctl restart dovecot
if [ $? -eq 0 ]; then
    print_success "Dovecot restarted successfully."
else
    print_error "Failed to restart Dovecot."
    exit 1
fi

# Configure Nginx to listen on port 443 (HTTPS)
print_section "Configuring Nginx to listen on port 443 (HTTPS)"

# Create self-signed SSL certificate
print_info "Creating self-signed SSL certificate..."
mkdir -p /etc/nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/nginx/ssl/nginx.key \
    -out /etc/nginx/ssl/nginx.crt \
    -subj "/C=US/ST=Texas/L=Austin/O=a-d-a-p-t.ai/CN=mail.a-d-a-p-t.ai"
if [ $? -eq 0 ]; then
    print_success "Self-signed SSL certificate created successfully."
else
    print_error "Failed to create self-signed SSL certificate."
    exit 1
fi

# Backup original configuration
cp /etc/nginx/sites-available/default /etc/nginx/sites-available/default.bak
print_info "Original Nginx configuration backed up to /etc/nginx/sites-available/default.bak."

# Create Nginx configuration
print_info "Creating Nginx configuration..."
cat > /etc/nginx/sites-available/default << EOF
server {
    listen 80;
    listen [::]:80;
    server_name mail.a-d-a-p-t.ai;

    # Redirect HTTP to HTTPS
    return 301 https://\$host\$request_uri;
}

server {
    listen 443 ssl;
    listen [::]:443 ssl;
    server_name mail.a-d-a-p-t.ai;

    ssl_certificate /etc/nginx/ssl/nginx.crt;
    ssl_certificate_key /etc/nginx/ssl/nginx.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-SHA384;

    root /var/www/html;
    index index.html;

    location / {
        try_files \$uri \$uri/ =404;
    }
}
EOF
print_success "Nginx configuration created."

# Create a simple index.html file
print_info "Creating index.html file..."
cat > /var/www/html/index.html << EOF
<!DOCTYPE html>
<html>
<head>
    <title>mail.a-d-a-p-t.ai</title>
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
        <h1>Welcome to mail.a-d-a-p-t.ai</h1>
        <p>This is the mail server for a-d-a-p-t.ai.</p>
        <p>For more information, please contact the administrator.</p>
    </div>
</body>
</html>
EOF
print_success "Index.html file created."

# Restart Nginx
print_info "Restarting Nginx..."
systemctl restart nginx
if [ $? -eq 0 ]; then
    print_success "Nginx restarted successfully."
else
    print_error "Failed to restart Nginx."
    exit 1
fi

# Check if all services are running
print_section "Checking service status"
if systemctl is-active --quiet nginx; then
    print_success "Nginx is running."
else
    print_error "Nginx is not running."
fi

if systemctl is-active --quiet dovecot; then
    print_success "Dovecot is running."
else
    print_error "Dovecot is not running."
fi

if systemctl is-active --quiet postfix; then
    print_success "Postfix is running."
else
    print_error "Postfix is not running."
fi

# Check if ports are open
print_section "Checking mail server ports"
print_info "Running check_mail_ports.sh script..."
./check_mail_ports.sh

print_section "Summary"
print_info "Mail services have been configured to listen on all required ports."
print_info "The following services are now running:"
print_info "- Nginx (ports 80 and 443)"
print_info "- Dovecot (ports 143, 993, 110, 995, and 4190)"
print_info "- Postfix (ports 25, 465, and 587)"
print_info "Note: If any ports are still closed, please check the service configuration."