import smtplib

EMAIL_MSG = """
Subject: {} finished
From: Laundry Notifier <{}>
To: {}

{} finished in {}
"""


class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email

        self.should_notify = True


    def notify(self, credentials, machine):
        from_addr = credentials["user"]
        with smtplib.SMTP_SSL(credentials["host"], credentials["port"]) as server:
            server.login(credentials["user"], credentials["password"])
            server.sendmail(from_addr, self.email, EMAIL_MSG.format(machine.name, from_addr,
                self.email, machine.name, machine.get_running_time()))
