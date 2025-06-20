FROM python:3.11-slim

WORKDIR /app
COPY cert_dashboard/ ./cert_dashboard/

RUN pip install -r cert_dashboard/requirements.txt

EXPOSE 8501
CMD ["streamlit", "run", "cert_dashboard/app.py", "--server.enableCORS=false"]
