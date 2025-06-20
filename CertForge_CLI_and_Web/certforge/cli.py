
import click
from cert_core import generate_certificate, export_certificate

@click.group()
def cli():
    pass

@cli.command()
@click.option('--type', type=click.Choice(['personal', 'business', 'code-sign']), required=True)
@click.option('--name', required=True)
@click.option('--email', required=False)
@click.option('--output', required=True)
@click.option('--password', required=False)
def create(type, name, email, output, password):
    cert, key = generate_certificate(cert_type=type, name=name, email=email)
    export_certificate(cert, key, output, password)
    print(f"Certificate created and saved to {output}")

if __name__ == "__main__":
    cli()
