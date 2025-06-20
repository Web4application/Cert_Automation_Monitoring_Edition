import smtplib
from email.message import EmailMessage

def send_certificate_email(to_email, attachment_path):
    msg = EmailMessage()
    msg['Subject'] = 'Your Digital Certificate'
    msg['From'] = 'certforge@gmail.com'
    msg['To'] = to_email
    msg.set_content('Attached is your certificate.')

    with open(attachment_path, 'rb') as f:
        msg.add_attachment(f.read(), maintype='application', subtype='x-pem-file', filename=attachment_path)

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login('certforge@gmail.com', 'testpassword123')  # Replace with real credentials
        server.send_message(msg)
