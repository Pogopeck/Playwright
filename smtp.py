import smtplib
from email.mime.text import MIMEText

# SMTP configuration
SMTP_SERVER = "139.7.95.72"
SMTP_PORT = 25  # Default SMTP port
SMTP_SENDER = "Playwright"
SMTP_RECEIVER = "chandan.sahoo@vodafone.com"

# Create the email message
msg = MIMEText("This is a test email sent using smtplib.")
msg["Subject"] = "Test Email from Playwright"
msg["From"] = SMTP_SENDER
msg["To"] = SMTP_RECEIVER

# Send the email
try:
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.sendmail(SMTP_SENDER, [SMTP_RECEIVER], msg.as_string())
    print("Email sent successfully.")
except Exception as e:
    print(f"Failed to send email: {e}")
