import base64
import smtplib
from email.mime.text import MIMEText

EMAIL_SUBJECT = "{} finished"
EMAIL_BODY = EMAIL_SUBJECT + " in {}"


class User:
    def __init__(self, name, email, notify=False):
        self.name = name
        self.email = email
        self.should_notify = notify


    def notify(self, credentials, machine):
        msg = MIMEText(EMAIL_BODY.format(machine.name, machine.get_running_time_str()))
        msg["Subject"] = EMAIL_SUBJECT.format(machine.name)
        msg["From"] = "Laundry Notifier <{}>".format(credentials["user"])
        msg["To"] = self.email

        password = credentials.get("password")
        if not password and "password_base64" in credentials:
            password = base64.b64decode(credentials["password_base64"]).decode()

        with smtplib.SMTP_SSL(credentials["host"], credentials["port"]) as server:
            server.login(credentials["user"], password)
            server.send_message(msg)
