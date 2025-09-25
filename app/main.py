from fastapi import FastAPI, Request, Form
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import json, os, subprocess
from datetime import datetime
import requests

app = FastAPI(title="WEB4 Analytics Control + SSL Dashboard")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

PANELS_FILE = "panels.json"
CERT_API_URL = "http://localhost:5000/api/certs"  # Example CertForge API endpoint

def load_panels():
    if os.path.exists(PANELS_FILE):
        with open(PANELS_FILE, "r") as f:
            return json.load(f)
    return {}

def get_ssl_info(domain):
    try:
        resp = requests.get(f"{CERT_API_URL}/{domain}")
        if resp.status_code == 200:
            data = resp.json()
            return {
                "valid": data.get("valid", False),
                "expiry": data.get("expiry", "N/A")
            }
    except Exception:
        pass
    return {"valid": False, "expiry": "N/A"}

@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    panels = load_panels()
    for domain, info in panels.items():
        ssl_info = get_ssl_info(domain)
        info["ssl_valid"] = ssl_info["valid"]
        info["ssl_expiry"] = ssl_info["expiry"]
    return templates.TemplateResponse("index.html", {"request": request, "panels": panels})

@app.post("/panel/{domain}/action")
def control_panel(domain: str, action: str = Form(...)):
    container_name = domain.replace(".", "_")
    if action not in ["start", "stop", "restart"]:
        return JSONResponse({"error": "Invalid action"}, status_code=400)
    try:
        subprocess.run(["docker", action, container_name], check=True)
        return JSONResponse({"status": f"{action} executed for {domain}"})
    except subprocess.CalledProcessError:
        return JSONResponse({"error": "Failed to execute action"}, status_code=500)

@app.get("/panel/{domain}/logs")
def panel_logs(domain: str):
    container_name = domain.replace(".", "_")
    try:
        logs = subprocess.check_output(["docker", "logs", "--tail", "100", container_name]).decode()
        return JSONResponse({"logs": logs})
    except subprocess.CalledProcessError:
        return JSONResponse({"error": "Cannot fetch logs"}, status_code=500)

@app.post("/panel/{domain}/email_test")
def email_test(domain: str):
    panels = load_panels()
    panel = panels.get(domain)
    if not panel:
        return JSONResponse({"error": "Panel not found"}, status_code=404)
    # Implement actual SMTP send logic here
    return JSONResponse({"status": f"Test email sent for {domain} (mocked)"})
