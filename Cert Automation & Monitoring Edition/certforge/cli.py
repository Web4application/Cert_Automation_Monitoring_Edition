
import click
from cert_core import generate_certificate, export_certificate
from signer import sign_file
from mailer import send_certificate_email

@click.group()
def cli():
    pass

@cli.command()
@click.option('--type', type=click.Choice(['personal', 'business', 'code-sign']), required=True)
@click.option('--name', required=True)
@click.option('--email', required=False)
@click.option('--output', required=True)
@click.option('--password', required=False)
@click.option('--send', is_flag=True, help="Email the certificate after generation")
def create(type, name, email, output, password, send):
    cert, key = generate_certificate(cert_type=type, name=name, email=email)
    export_certificate(cert, key, output, password)
    print(f"Certificate saved to {output}")
    if send and email:
        send_certificate_email(email, output)

@cli.command()
@click.option('--cert', required=True)
@click.option('--password', required=False)
@click.option('--input', 'input_file', required=True)
def sign(cert, password, input_file):
    sign_file(cert_path=cert, password=password, file_path=input_file)

if __name__ == "__main__":
    cli()
