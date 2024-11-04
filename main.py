# main.py
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import os
import json
from pathlib import Path
import shutil

app = FastAPI()

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Store active sites in a JSON file
SITES_FILE = "active_sites.json"
NGINX_SITES_PATH = "/etc/nginx/sites-enabled"
NGINX_TEMPLATE_PATH = "nginx_site_template.conf"

def load_active_sites():
    if not os.path.exists(SITES_FILE):
        return {}
    with open(SITES_FILE, 'r') as f:
        return json.load(f)

def save_active_sites(sites):
    with open(SITES_FILE, 'w') as f:
        json.dump(sites, f)

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open('static/index.html', 'r') as f:
        return f.read()

@app.get("/api/active_sites")
async def active_sites():
    return load_active_sites()

@app.post("/api/deploy")
async def deploy(site_name: str, port: int):
    sites = load_active_sites()
    if site_name in sites:
        raise HTTPException(status_code=400, detail="Site already exists")
        
    # Create nginx config from template
    with open(NGINX_TEMPLATE_PATH, 'r') as f:
        template = f.read()
    
    config = template.format(
        site_name=site_name,
        port=port
    )
    
    # Write nginx config
    config_path = os.path.join(NGINX_SITES_PATH, f"{site_name}.conf")
    with open(config_path, 'w') as f:
        f.write(config)
    
    # Update active sites
    sites[site_name] = port
    save_active_sites(sites)
    
    # Reload nginx
    os.system("nginx -s reload")
    
    return {"status": "success"}

@app.post("/api/remove")
async def remove(site_name: str):
    sites = load_active_sites()
    
    if site_name not in sites:
        raise HTTPException(status_code=404, detail="Site not found")
    
    # Remove nginx config
    config_path = os.path.join(NGINX_SITES_PATH, f"{site_name}.conf")
    if os.path.exists(config_path):
        os.remove(config_path)
    
    # Remove from active sites
    del sites[site_name]
    save_active_sites(sites)
    
    # Reload nginx
    os.system("nginx -s reload")
    
    return {"status": "success"}