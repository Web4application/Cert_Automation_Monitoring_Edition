from fastapi import FastAPI, Request, Form
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import json, os, subprocess, requests
from datetime import datetime, timedelta

ALERT_SSL_DAYS = 30

app = FastAPI(title="WEB4 Analytics Cockpit")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

PANELS_FILE = "panels.json"
CERT_API_URL = "http://cert_automation:5000/api/certs"

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
            return {"valid": data.get("valid", False), "expiry": data.get("expiry", "N/A")}
    except Exception:
        pass
    return {"valid": False, "expiry": "N/A"}

def load_panels_with_status():
    panels = load_panels()
    for domain, info in panels.items():
        ssl_info = get_ssl_info(domain)
        info["ssl_valid"] = ssl_info["valid"]
        info["ssl_expiry"] = ssl_info["expiry"]
        try:
            info["ssl_expiry_date"] = datetime.strptime(info["ssl_expiry"], "%Y-%m-%d")
        except Exception:
            info["ssl_expiry_date"] = None
        container_name = domain.replace(".", "_")
        try:
            result = subprocess.run(
                ["docker", "inspect", "-f", "{{.State.Running}}", container_name],
                capture_output=True, text=True
            )
            info["container_running"] = "true" in result.stdout.lower()
        except subprocess.CalledProcessError:
            info["container_running"] = False
    return panels

@app.get("/", response_class=HTMLResponse)
def dashboard_page(request: Request):
    panels = load_panels_with_status()
    return templates.TemplateResponse("index.html", {"request": request, "panels": panels, "now": datetime.utcnow()})

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

@app.get("/alerts")
def get_alerts():
    panels = load_panels_with_status()
    alerts = []
    now = datetime.utcnow()
    for domain, info in panels.items():
        if info.get("ssl_expiry_date"):
            days_left = (info["ssl_expiry_date"] - now).days
            if days_left <= 30:
                alerts.append(f"⚠ SSL for {domain} expires in {days_left} day(s)")
        if not info.get("container_running", False):
            alerts.append(f"❌ Panel {domain} is stopped")
    return JSONResponse({"alerts": alerts})
