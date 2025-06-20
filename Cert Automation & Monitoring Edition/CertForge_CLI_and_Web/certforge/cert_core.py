
from cryptography import x509
from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from datetime import datetime, timedelta

def generate_certificate(cert_type, name, email=None):
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, name),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Fadaka CA"),
    ])
    if email:
        subject = issuer = x509.Name(subject.rdns + [x509.NameAttribute(NameOID.EMAIL_ADDRESS, email)])
    cert_builder = x509.CertificateBuilder().subject_name(subject).issuer_name(
        issuer).public_key(key.public_key()).serial_number(
        x509.random_serial_number()).not_valid_before(
        datetime.utcnow()).not_valid_after(
        datetime.utcnow() + timedelta(days=365))
    if cert_type == "code-sign":
        cert_builder = cert_builder.add_extension(
            x509.ExtendedKeyUsage([ExtendedKeyUsageOID.CODE_SIGNING]), critical=False)
    cert = cert_builder.sign(key, hashes.SHA256(), default_backend())
    return cert, key

def export_certificate(cert, key, filename, password=None):
    if password:
        encryption = serialization.BestAvailableEncryption(password.encode())
    else:
        encryption = serialization.NoEncryption()
    with open(filename, "wb") as f:
        f.write(key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=encryption,
        ))
        f.write(cert.public_bytes(serialization.Encoding.PEM))
