import smtplib
import os
from email.mime.text import MIMEText


def send_email_reminder(receiver_email, event_title):

    sender_email = os.getenv("EMAIL_ADDRESS")
    app_password = os.getenv("EMAIL_PASSWORD")

    if not sender_email or not app_password:
        return

    msg = MIMEText(f"Reminder: You have an event '{event_title}' coming up.")
    msg["Subject"] = "Event Reminder"
    msg["From"] = sender_email
    msg["To"] = receiver_email

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, app_password)

        server.sendmail(sender_email, receiver_email, msg.as_string())

        server.quit()
    except:
        pass