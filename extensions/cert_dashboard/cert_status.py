from cryptography import x509
from cryptography.hazmat.backends import default_backend
from datetime import datetime
import os

def get_cert_expiry(path):
    with open(path, 'rb') as f:
        data = f.read()
        cert = x509.load_pem_x509_certificate(data, default_backend())
        return cert.not_valid_after

def check_cert_status(cert_path):
    expiry = get_cert_expiry(cert_path)
    remaining = (expiry - datetime.utcnow()).days
    print(f"📜 Cert expires on: {expiry} ({remaining} days remaining)")
    if remaining < 15:
        print("⚠️ Warning: Certificate expires soon!")
    elif remaining < 0:
        print("❌ Certificate is expired!")

# Example usage
if __name__ == "__main__":
    check_cert_status("certs/DeviceCert.cer")
