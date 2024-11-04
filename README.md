# Hosting Service

This is a proof-of-concept for a web server which can map another server, running on a different port, to a subdomain.

## Setup

1. Setup the hosting service server
    1. Add executable permissions to setup with `chmod +x setup.sh`
    2. Run `sudo ./setup.sh` to:
        - Download nginx and copy `nginx/nginx.conf` to `/etc/nginx/nginx.conf`
        - Create the directory `/etc/nginx/sites-enabled` for client configurations
        - Download dnsmasq and copy `dnsmasq/dnsmasq.conf` to `/etc/dnsmasq.conf` so all subdomains are mapped to localhost
        - Download python dependencies
        - Run the server with `uvicorn main:app --reload`

2. Setup the client server
    1. Download the [React Template](https://github.com/granawkins/react-template) repo
    2. Run `npm install` to install the dependencies
    3. Run dev server with `npm run dev`

3. Go to hosting server at http://localhost

4. Add the client site by entering `react-template` as the site name and `5173` as the port

## How it works

### Add and remove full servers (not just static sites) on the fly
We assume the project is already running on some port on localhost Create a new nginx config using the `nginx_site_template.conf` and add it to `/etc/nginx/sites-enabled`. Then restart nginx. Our main nginx.conf will pull in all configs there and route subdomain requests to the correct port.

We also need to map all subdomains to localhost (127.0.0.1) so we can route to them. We do this locally with dnsmasq. For deployment, we can add a wildcard domain (*.mentat.ai) to the DNS record.

### Preview sites in an iframe and take screenshots
The HTTP protocol really doesn't want server taking a screenshot of the iframe. Instead we add a 'take screenshot' script to the client server and call it from host via a message. 