import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_Email(candidate_email,candidate_role,candidate_name) :

    # Email configuration
    SMTP_SERVER = 'smtp.gmail.com'
    SMTP_PORT = 587
    SMTP_USERNAME = 'thormadhesh27@gmail.com'
    SMTP_PASSWORD = 'reyg ushk kjhx emas'
    RECIPIENT_EMAIL = candidate_email

    # Create message
    msg = MIMEMultipart()
    msg['From'] = SMTP_USERNAME
    msg['To'] = RECIPIENT_EMAIL
    msg['Subject'] = 'Interview'
    body = f"Dear {candidate_name}, \n You are Shortlisted For {candidate_role} role \n Interview Link:"
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Establish SMTP connection
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # Upgrade the connection to TLS
        server.login(SMTP_USERNAME, SMTP_PASSWORD)

        # Send email
        server.sendmail(SMTP_USERNAME, RECIPIENT_EMAIL, msg.as_string())
        email_status = 'sent'

        # Close SMTP connection
        server.quit()
    except Exception as e:
        print(f'Error sending email: {e}')

    return email_status
