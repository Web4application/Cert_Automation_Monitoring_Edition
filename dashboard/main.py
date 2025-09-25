from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import json
import os
import subprocess

app = FastAPI(title="WEB4 Analytics Control UI")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

PANELS_FILE = "panels.json"

def load_panels():
    if os.path.exists(PANELS_FILE):
        with open(PANELS_FILE, "r") as f:
            return json.load(f)
    return {}

@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    panels = load_panels()
    return templates.TemplateResponse("index.html", {"request": request, "panels": panels})

@app.get("/panel/{domain}")
def get_panel(domain: str):
    panels = load_panels()
    panel = panels.get(domain)
    if panel:
        return JSONResponse(content=panel)
    return JSONResponse(content={"error": "Panel not found"}, status_code=404)

@app.post("/panel/{domain}/action")
def control_panel(domain: str, action: str):
    container_name = domain.replace(".", "_")
    if action not in ["start", "stop", "restart"]:
        return JSONResponse(content={"error": "Invalid action"}, status_code=400)
    try:
        subprocess.run(["docker", action, container_name], check=True)
        return JSONResponse(content={"status": f"{action} executed for {domain}"})
    except subprocess.CalledProcessError:
        return JSONResponse(content={"error": "Failed to execute action"}, status_code=500)

      function control(domain, action) {
    fetch(`/panel/${domain}/action`, {
        method: "POST",
        headers: {"Content-Type": "application/x-www-form-urlencoded"},
        body: new URLSearchParams({action: action})
    })
    .then(res => res.json())
    .then(data => alert(JSON.stringify(data)))
    .catch(err => alert("Error: " + err));
}

function showLogs(domain) {
    fetch(`/panel/${domain}/logs`)
    .then(res => res.json())
    .then(data => {
        document.getElementById("logs").textContent = data.logs || data.error;
    });
}

function testEmail(domain) {
    fetch(`/panel/${domain}/email_test`, {method: "POST"})
    .then(res => res.json())
    .then(data => alert(JSON.stringify(data)));
}
