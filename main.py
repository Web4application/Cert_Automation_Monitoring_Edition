from fastapi import FastAPI, Form, Request, Depends
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import sqlite3, qrcode, os
from cert_core import generate_certificate, export_certificate
from mailer import send_certificate_email

app = FastAPI()
security = HTTPBasic()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

DB_PATH = "cert_logs.db"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS certs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT, email TEXT, type TEXT, filename TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
init_db()

def is_admin(credentials: HTTPBasicCredentials = Depends(security)):
    return credentials.username == ADMIN_USERNAME and credentials.password == ADMIN_PASSWORD

@app.get("/", response_class=HTMLResponse)
async def form(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})

@app.post("/generate")
async def generate(name: str = Form(...), email: str = Form(None), type: str = Form(...), password: str = Form(None)):
    cert, key = generate_certificate(cert_type=type, name=name, email=email)
    filename = f"{name.replace(' ', '_')}_cert.pem"
    filepath = f"static/{filename}"
    export_certificate(cert, key, filepath, password)

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("INSERT INTO certs (name, email, type, filename) VALUES (?, ?, ?, ?)",
                     (name, email, type, filepath))

    if email:
        send_certificate_email(email, filepath)

    # QR code
    qr_path = f"static/{name.replace(' ', '_')}_qr.png"
    qr = qrcode.make(f"http://localhost:8000/{filepath}")
    qr.save(qr_path)

    return FileResponse(filepath, filename=filename)

@app.get("/admin", response_class=HTMLResponse)
async def admin_panel(request: Request, auth: bool = Depends(is_admin)):
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute("SELECT * FROM certs ORDER BY created_at DESC").fetchall()
    return templates.TemplateResponse("admin.html", {"request": request, "certs": rows})
