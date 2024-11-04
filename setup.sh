#!/bin/bash

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root"
    exit
fi

# Install required packages
apt-get update
apt-get install -y nginx python3-pip dnsmasq

# Install Python dependencies
pip3 install -r requirements.txt

# Configure dnsmasq for wildcard localhost
cat > /etc/dnsmasq.conf << EOL
listen-address=127.0.0.1
no-hosts
address=/.localhost/127.0.0.1
local=/localhost/
domain-needed
bogus-priv
EOL

# Configure system resolver
cat > /etc/systemd/resolved.conf << EOL
[Resolve]
DNS=127.0.0.1
Domains=~localhost
EOL

# Create necessary directories
mkdir -p /etc/nginx/sites-enabled
chmod 755 /etc/nginx/sites-enabled

# Copy nginx configuration
cp -f nginx/nginx.conf /etc/nginx/nginx.conf

# Restart services
systemctl restart systemd-resolved
systemctl restart dnsmasq
systemctl restart nginx

# Start the FastAPI application
uvicorn main:app --host 0.0.0.0 --port 8000