import os
from pathlib import Path
from datetime import datetime, timedelta
from cryptography import x509
from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

# -----------------------------
# Helper Functions
# -----------------------------
def generate_rsa_key(key_size=2048):
    return rsa.generate_private_key(public_exponent=65537, key_size=key_size, backend=default_backend())

def create_ca_certificate(name, key, valid_days=3650):
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, name),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "WEB4 CA"),
    ])
    cert_builder = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.utcnow() - timedelta(days=1))
        .not_valid_after(datetime.utcnow() + timedelta(days=valid_days))
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
    )
    return cert_builder.sign(key, hashes.SHA256(), default_backend())

def create_signed_certificate(ca_cert, ca_key, common_name, cert_type=None, email=None, san_list=None, valid_days=365):
    key = generate_rsa_key()
    subject_attrs = [
        x509.NameAttribute(NameOID.COMMON_NAME, common_name),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "WEB4"),
    ]
    if email:
        subject_attrs.append(x509.NameAttribute(NameOID.EMAIL_ADDRESS, email))
    subject = x509.Name(subject_attrs)

    if san_list is None:
        san_list = [common_name]

    cert_builder = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(ca_cert.subject)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.utcnow() - timedelta(days=1))
        .not_valid_after(datetime.utcnow() + timedelta(days=valid_days))
        .add_extension(x509.SubjectAlternativeName([x509.DNSName(name) for name in san_list]), critical=False)
    )

    if cert_type == "code-sign":
        cert_builder = cert_builder.add_extension(
            x509.ExtendedKeyUsage([ExtendedKeyUsageOID.CODE_SIGNING]), critical=False
        )

    return cert_builder.sign(ca_key, hashes.SHA256(), default_backend()), key

def export_key_cert(key, cert, key_file, cert_file, bundle_file=None):
    enc = serialization.NoEncryption()
    key_bytes = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=enc
    )
    cert_bytes = cert.public_bytes(serialization.Encoding.PEM)
    with open(key_file, "wb") as f: f.write(key_bytes)
    with open(cert_file, "wb") as f: f.write(cert_bytes)
    if bundle_file:
        with open(bundle_file, "wb") as f: f.write(key_bytes + cert_bytes)

# -----------------------------
# Main Function
# -----------------------------
def main():
    # Environment variables
    ca_name = os.environ.get("WEB4_CA_NAME", "WEB4 Root CA")
    code_name = os.environ.get("WEB4_CODE_NAME", "WEB4 Dev")
    server_name = os.environ.get("WEB4_SERVER_NAME", "myserver.web4.com")
    server_sans = os.environ.get("WEB4_SERVER_SANS", server_name).split(",")

    out_dir = Path("web4_certs")
    out_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    # 1️⃣ Generate root CA
    ca_key = generate_rsa_key()
    ca_cert = create_ca_certificate(ca_name, ca_key)
    export_key_cert(
        ca_key, ca_cert,
        key_file=out_dir / f"ca_key_{timestamp}.pem",
        cert_file=out_dir / f"ca_cert_{timestamp}.pem"
    )
    print(f"Root CA generated: {out_dir / f'ca_cert_{timestamp}.pem'}")

    # 2️⃣ Generate code-signing certificate
    code_cert, code_key = create_signed_certificate(ca_cert, ca_key, code_name, cert_type="code-sign")
    export_key_cert(
        code_key, code_cert,
        key_file=out_dir / f"code_key_{timestamp}.pem",
        cert_file=out_dir / f"code_cert_{timestamp}.pem",
        bundle_file=out_dir / f"code_bundle_{timestamp}.pem"
    )
    print(f"Code-signing certificate generated with bundle in {out_dir}")

    # 3️⃣ Generate server certificate
    server_cert, server_key = create_signed_certificate(ca_cert, ca_key, server_name, san_list=server_sans)
    export_key_cert(
        server_key, server_cert,
        key_file=out_dir / f"server_key_{timestamp}.pem",
        cert_file=out_dir / f"server_cert_{timestamp}.pem",
        bundle_file=out_dir / f"server_bundle_{timestamp}.pem"
    )
    print(f"Server certificate generated with bundle in {out_dir}")

if __name__ == "__main__":
    main()
