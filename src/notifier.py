import logging
import threading
import time
from typing import Any, Dict, List

import plugins
from machine import Machine
from user import User


class LaundryNotifier:
    def __init__(self, config: Dict[str, Any]):
        self.stop_event = threading.Event()
        self.smtp_credentials = config["smtp_credentials"]

        adc_model = config["adc_model"].upper()
        self.machines = [Machine(adc_model, **args) for args in config["machines"]]
        self.users = [User(self, **args) for args in config["users"]]

        self.plugins = {name: plugins.load(name, self, config) for name in config["plugins"]}
        assert self.validate_plugins(config)


    @property
    def stopped(self) -> bool:
        return self.stop_event.is_set()


    def validate_plugins(self, config: Dict[str, Any]) -> bool:
        result = True
        for plugin_name, plugin in self.plugins.items():
            error = plugin.validate(config)
            if error:
                logging.error("[{}] {}".format(plugin_name, error))
                result = False
        return result


    def start(self) -> None:
        self.stop_event.clear()
        threading.Thread(target=self.watch_machines).start()
        for plugin in self.plugins.values():
            plugin.start()


    def stop(self) -> None:
        self.stop_event.set()
        for plugin in self.plugins.values():
            plugin.stop()


    def notify(self, machine: Machine) -> None:
        for user in self.users:
            if machine.name in user.notify_machines:
                user.notify(self.smtp_credentials, machine)


    def on_machine_status_changed(self, machine: Machine) -> None:
        if not machine.is_on:
            self.notify(machine)

        status_str = "ON" if machine.is_on else "OFF"
        logging.info("[{}] Status changed to {}".format(machine.name, status_str))


    def watch_machines(self) -> None:
        while not self.stopped:
            for machine in self.machines:
                if machine.update():
                    self.on_machine_status_changed(machine)

            time.sleep(0.1)
