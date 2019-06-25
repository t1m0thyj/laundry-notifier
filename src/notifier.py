import logging
import threading
import time

import plugins
from machine import Machine
from user import User


class LaundryNotifier:
    def __init__(self, config):
        self.stop_event = threading.Event()
        self.smtp_credentials = config["smtp_credentials"]

        adc_model = config["adc_model"].upper()
        self.machines = [Machine(adc_model, **args) for args in config["machines"]]
        self.users = [User(**args) for args in config["users"]]

        self.plugins = [plugins.load(name, self, config) for name in config["plugins"]]
        assert self.validate_config(config)


    @property
    def stopped(self):
        return self.stop_event.is_set()


    def validate_config(self, config):
        result = True
        for plugin in self.plugins:
            error = plugin.validate_config(config)
            if error:
                logging.error(error)
                result = False
        return result


    def start(self):
        self.stop_event.clear()
        threading.Thread(target=self.watch_machines).start()
        for plugin in self.plugins:
            plugin.start()
        logging.info(self.get_notify_status())


    def stop(self):
        self.stop_event.set()
        for plugin in self.plugins:
            plugin.stop()


    def get_notify_status(self):
        user_list = self.users.filter(lambda user: user.should_notify)
        status_str = ", ".join([user.name for user in user_list]) if user_list else "OFF"
        return "Notify: {}".format(status_str)


    def notify(self, machine):
        for user in self.users:
            if user.should_notify:
                user.notify(self.smtp_credentials, machine)


    def on_machine_status_changed(self, machine):
        if not machine.is_on:
            self.notify(machine)

        logging.info("{}: {}".format(machine.name, "ON" if machine.is_on else "OFF"))


    def watch_machines(self):
        while not self.stopped:
            for machine in self.machines:
                if machine.update():
                    self.on_machine_status_changed(machine)

            time.sleep(0.1)
