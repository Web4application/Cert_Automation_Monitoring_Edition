from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, FileResponse
from cert_core import generate_certificate, export_certificate
import os

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def form():
    return '''
    <html>
        <body>
    <h2>Universal Certificate Generator</h2>
    <form action="/generate" method="post">
    Name: <input name="name"><br>
    Email (optional): <input name="email"><br>
    Certificate Type: <select name="type">
        <option>personal</option>
        <option>business</option>
        <option>code-sign</option>
    </select><br>
    Export Password (optional): <input name="password" type="password"><br>
    <input type="submit" value="Generate Certificate">
    </form>
    </body></html>
    '''

@app.post("/generate")
async def generate(name: str = Form(...), email: str = Form(None), type: str = Form(...), password: str = Form(None)):
    cert, key = generate_certificate(cert_type=type, name=name, email=email)
    output_path = f"{name.replace(' ', '_')}_certificate.pem"
    export_certificate(cert, key, output_path, password)
    return FileResponse(output_path, filename=output_path)
