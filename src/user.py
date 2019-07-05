import logging
import smtplib
from email.mime.text import MIMEText
from typing import Any, List, Optional, Set

from credentials import Credentials
from machine import Machine

EMAIL_SUBJECT = "{} finished"
EMAIL_BODY = EMAIL_SUBJECT + " in {}"


class User:
    def __init__(self, notifier: Any, name: str, email: str,
            notify_machines: Optional[List[str]]=None):
        self._notifier = notifier
        self.name = name
        self.email = email
        self.notify_machines = set()  # type: Set[str]

        for machine_name in (notify_machines or []):
            self.add_machine(machine_name)


    def add_machine(self, machine_name: str) -> None:
        if machine_name == "*":
            self.notify_machines = set([machine.name for machine in self._notifier.machines])
            logging.info("Subcribed user \"{}\" to all machines".format(self.name))
        else:
            self.notify_machines.add(machine_name)
            logging.info("Subcribed user \"{}\" to machine \"{}\"".format(self.name, machine_name))


    def notify(self, credentials: Credentials, machine: Machine) -> None:
        msg = MIMEText(EMAIL_BODY.format(machine.name, machine.get_running_time_str()))
        msg["Subject"] = EMAIL_SUBJECT.format(machine.name)
        msg["From"] = "Laundry Notifier <{}>".format(credentials.user)
        msg["To"] = self.email

        with smtplib.SMTP_SSL(credentials.host, credentials.port) as server:
            server.login(credentials.user, credentials.password)
            server.send_message(msg)

        logging.info("Notified user \"{}\"".format(self.name))


    def remove_machine(self, machine_name: str) -> None:
        if machine_name == "*":
            self.notify_machines.clear()
            logging.info("Unsubscribed user \"{}\" from all machines".format(self.name))
        else:
            self.notify_machines.remove(machine_name)
            logging.info("Unsubscribed user \"{}\" from machine \"{}\"".format(self.name, machine_name))
