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
        msg = MIMEText(EMAIL_BODY.format(machine.name, machine.get_running_time()))
        msg["Subject"] = EMAIL_SUBJECT.format(machine.name)
        msg["From"] = "Laundry Notifier <{}>".format(credentials["user"])
        msg["To"] = self.email

        with smtplib.SMTP_SSL(credentials["host"], credentials["port"]) as server:
            server.login(credentials["user"], credentials["password"])
            server.send_message(msg)
