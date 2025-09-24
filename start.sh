#!/bin/bash
set -e

# 1️⃣ Generate certificates if they do not exist
if [ -z "$(ls -A /app/web4_certs)" ]; then
    echo "Generating WEB4 certificates..."
    python /app/web4_env_cert.py
else
    echo "Certificates already exist, skipping generation."
fi

# 2️⃣ Start FastAPI app
echo "Starting FastAPI app..."
exec uvicorn web.main:app --host 0.0.0.0 --port 8000
