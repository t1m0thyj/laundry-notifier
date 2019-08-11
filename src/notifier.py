import logging
import threading
import time
from typing import Any, Dict, List

import plugins
from credentials import Credentials
from machine import Machine
from user import User


class LaundryNotifier:
    def __init__(self, config: Dict[str, Any]):
        self.stop_event = threading.Event()

        self.plugins = {name: plugins.load(name, self, config) for name in config["plugins"]}
        assert self.validate_plugins(config)

        self.smtp_credentials = Credentials("smtp", config)
        self.machines = [Machine(config["adc_config"], **args) for args in config["machines"]]
        self.users = [User(self, **args) for args in config["users"]]


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

        plugin_start_time = time.time()
        for plugin in self.plugins.values():
            plugin.start()

        if self.plugins:
            plugin_start_length = round(time.time() - plugin_start_time, 3)
            logging.info("Started {} plugin(s) in {} s".format(len(self.plugins),
                plugin_start_length))


    def stop(self) -> None:
        self.stop_event.set()
        for plugin in self.plugins.values():
            plugin.stop()


    def get_subscribed_users(self, machine: Machine) -> List[User]:
        return [user for user in self.users if machine.name in user.notify_machines]


    def on_machine_status_changed(self, machine: Machine) -> None:
        if not machine.is_on:
            for user in self.get_subscribed_users(machine):
                user.notify(self.smtp_credentials, machine)

        status_str = "ON" if machine.is_on else "OFF"
        logging.info("[{}] Status changed to {}".format(machine.name, status_str))


    def watch_machines(self) -> None:
        while not self.stopped:
            for machine in self.machines:
                if machine.update():
                    self.on_machine_status_changed(machine)

            time.sleep(0.1)
