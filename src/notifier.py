import logging
import threading
import time

from machine import Machine
from user import User


class LaundryNotifier:
    def __init__(self, config):
        self.should_stop = False
        self.smtp_credentials = config["smtp_credentials"]

        adc_model = config["adc_model"].upper()
        self.machines = [Machine(adc_model, **args) for args in config["machines"]]
        self.users = [User(**args) for args in config["users"]]


    def start(self):
        self.should_stop = False
        threading.Thread(target=self.watch_machines).start()


    def stop(self):
        self.should_stop = True


    def notify(self, machine):
        for user in self.users:
            if user.should_notify:
                user.notify(self.smtp_credentials, machine)


    def watch_machines(self):
        while not self.should_stop:
            for machine in self.machines:
                if machine.update():
                    if not machine.is_on:
                        self.notify(machine)
                        machine.started_time = -1

                    logging.info("{}: {}".format(machine.name, "ON" if machine.is_on else "OFF"))

            time.sleep(0.1)
