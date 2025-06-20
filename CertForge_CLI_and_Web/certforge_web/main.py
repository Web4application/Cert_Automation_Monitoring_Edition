
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, FileResponse
from cert_core import generate_certificate, export_certificate
import os

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def form():
    return '''
    <html><body>
    <form action="/generate" method="post">
    Name: <input name="name"><br>
    Email: <input name="email"><br>
    Cert Type: <select name="type"><option>personal</option><option>business</option><option>code-sign</option></select><br>
    Password (optional): <input name="password"><br>
    <input type="submit">
    </form>
    </body></html>
    '''

@app.post("/generate")
async def generate(name: str = Form(...), email: str = Form(None), type: str = Form(...), password: str = Form(None)):
    cert, key = generate_certificate(cert_type=type, name=name, email=email)
    output_path = f"{name.replace(' ', '_')}_cert.pem"
    export_certificate(cert, key, output_path, password)
    return FileResponse(output_path, filename=output_path)
