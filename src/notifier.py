import logging
import threading
import time

from machine import Machine
from user import User


class LaundryNotifier:
    def __init__(self, config):
        self.stop_event = threading.Event()
        self.smtp_credentials = config["smtp_credentials"]

        adc_model = config["adc_model"].upper()
        self.machines = [Machine(adc_model, **args) for args in config["machines"]]
        self.users = [User(**args) for args in config["users"]]


    def start(self):
        self.stop_event.clear()
        threading.Thread(target=self.watch_machines).start()


    def stop(self):
        self.stop_event.set()


    def notify(self, machine):
        for user in self.users:
            if user.should_notify:
                user.notify(self.smtp_credentials, machine)


    def on_machine_status_changed(self, machine):
        if not machine.is_on:
            self.notify(machine)

        logging.info("{}: {}".format(machine.name, "ON" if machine.is_on else "OFF"))


    def watch_machines(self):
        while not self.stop_event.is_set():
            for machine in self.machines:
                if machine.update():
                    self.on_machine_status_changed(machine)

            time.sleep(0.1)
