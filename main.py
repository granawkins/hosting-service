from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import os
import json

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

BASE_URL = "localhost"
SITES_FILE = "active_sites.json"
NGINX_SITES_PATH = "/etc/nginx/sites-enabled"
NGINX_TEMPLATE_PATH = "nginx/nginx_site_template.conf"


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
async def deploy(request: Request):
    data = await request.json()
    site_name = data.get("site_name")
    port = data.get("port")
    sites = load_active_sites()
    if site_name in sites:
        raise HTTPException(status_code=400, detail="Site already exists")

    # Create an nginx config, add to sites-enabled and reload nginx
    with open(NGINX_TEMPLATE_PATH, 'r') as f:
        template = f.read()
    config = template.format(
        server_name=f"{site_name}.{BASE_URL}",
        port=port
    )
    config_path = os.path.join(NGINX_SITES_PATH, f"{site_name}.conf")
    with open(config_path, 'w') as f:
        f.write(config)
    os.system("nginx -s reload")

    sites[site_name] = port
    save_active_sites(sites)
    return {"status": "success"}


@app.post("/api/remove")
async def remove(request: Request):
    data = await request.json()
    site_name = data.get("site_name")
    sites = load_active_sites()
    if site_name not in sites:
        raise HTTPException(status_code=404, detail="Site not found")
    
    # Remove nginx config
    config_path = os.path.join(NGINX_SITES_PATH, f"{site_name}.conf")
    if os.path.exists(config_path):
        os.remove(config_path)
    os.system("nginx -s reload")

    del sites[site_name]
    save_active_sites(sites)
    return {"status": "success"}