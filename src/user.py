import smtplib

EMAIL_BODY = "{} finished in {}"

EMAIL_MSG = """
Subject: {} finished
From: Laundry Notifier <{}>
To: {}

{}
"""


class User:
    def __init__(self, name, email, notify=True, send_sms=False):
        self.name = name
        self.email = email
        self.should_notify = notify
        self.send_sms = send_sms


    def notify(self, credentials, machine):
        from_addr = credentials["user"]
        with smtplib.SMTP_SSL(credentials["host"], credentials["port"]) as server:
            server.login(credentials["user"], credentials["password"])

            msg = EMAIL_BODY.format(machine.name, machine.get_running_time())
            if not self.send_sms:
                msg = EMAIL_MSG.format(machine.name, from_addr, self.email, msg)

            server.sendmail(from_addr, self.email, msg)
