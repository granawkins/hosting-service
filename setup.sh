#!/bin/bash

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root"
    exit
fi

# Install required packages
apt-get update
apt-get install -y nginx python3-pip

# Install Python dependencies
pip3 install -r requirements.txt

# Create necessary directories
mkdir -p /etc/nginx/sites-enabled
chmod 755 /etc/nginx/sites-enabled

# Copy nginx configuration
cp -f nginx/nginx.conf /etc/nginx/nginx.conf
cp -f nginx/nginx_site_template.conf ./nginx_site_template.conf

# Ensure nginx sites-enabled exists and is empty
rm -f /etc/nginx/sites-enabled/*

# Restart nginx (will start if not running)
systemctl restart nginx

# Start the FastAPI application
uvicorn main:app --host 0.0.0.0 --port 8000