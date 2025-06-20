# ProjectPilotAI - Automation Targets

.PHONY: install dev run-dashboard cert-run lint

install:
    pip install -r requirements.txt

dev:
    pip install -r requirements-dev.txt

run-dashboard:
    cd extensions/cert_dashboard && streamlit run app.py

cert-run:
    powershell -ExecutionPolicy Bypass -File extensions/cert_automation/auto_cert.ps1

lint:
    flake8 extensions/cert_dashboard/
