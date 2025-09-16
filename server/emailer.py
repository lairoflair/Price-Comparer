import smtplib
from email.mime.text import MIMEText

# Example email alert function
def send_email_alert(to_email, subject, body):
    from_email = "your@email.com"
    password = "yourpassword"  # Use environment variable in production
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(from_email, password)
        server.sendmail(from_email, [to_email], msg.as_string())

# Replace credentials and SMTP server as needed
