import base64
import logging
import smtplib
from email.mime.text import MIMEText

EMAIL_SUBJECT = "{} finished"
EMAIL_BODY = EMAIL_SUBJECT + " in {}"


class User:
    def __init__(self, notifier, name, email, notify_machines=None):
        self._notifier = notifier
        self.name = name
        self.email = email
        self.notify_machines = set()

        for machine_name in (notify_machines or []):
            self.add_machine(machine_name)


    def add_machine(self, machine_name):
        if machine_name == "*":
            self.notify_machines = set(self._notifier.machines)
            logging.info("Subcribed user \"{}\" to all machines".format(self.name))
        else:
            self.notify_machines.add(machine_name)
            logging.info("Subcribed user \"{}\" to machine \"{}\"".format(self.name, machine_name))


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

        logging.info("Notified user \"{}\"".format(self.name))


    def remove_machine(self, machine_name):
        if machine_name == "*":
            self.notify_machines.clear()
            logging.info("Unsubscribed user \"{}\" from all machines")
        else:
            self.notify_machines.remove(machine_name)
            logging.info("Unsubscribed user \"{}\" from machine \"{}\"".format(self.name, machine_name))
