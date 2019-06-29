from typing import Any, Dict, Optional

from gpiozero import Button  # pylint: disable=import-error

BUTTON_PIN = 5


class Plugin:
    def __init__(self, notifier: Any, config: Dict[str, Any]):
        self._notifier = notifier
        self.button = Button(BUTTON_PIN, pull_up=True, bounce_time=0.1)
        self.button_long_pressed = False
        self.current_user = -1


    def validate(self, config: Dict[str, Any]) -> Optional[str]:
        if not config.get("users"):
            return "At least one user required in config.json"

        if len([user for user in config["users"] if user.get("notify_machines")]) > 1:
            return "Only one user can have notify_machines listed in config.json"

        return None


    def start(self) -> None:
        for i, user in enumerate(self._notifier.users):
            if user.notify_machines:
                self.current_user = i
                break

        self.button.when_held = self.on_button_held
        self.button.when_pressed = self.on_button_pressed
        self.button.when_released = self.on_button_released


    def stop(self) -> None:
        self.button.when_held = None
        self.button.when_pressed = None
        self.button.when_released = None


    def handle_button_press(self) -> None:
        if self.button_long_pressed or (len(self._notifier.users) == 1 and
                self._notifier.users[0].notify_machines):
            self.current_user = -1
        else:
            self.current_user += 1
            if self.current_user >= len(self._notifier.users):
                self.current_user = 0

        for i in range(len(self._notifier.users)):
            if i == self.current_user:
                self._notifier.users[i].add_machine("*")
            else:
                self._notifier.users[i].remove_machine("*")


    def on_button_held(self) -> None:
        if len(self._notifier.users) > 1:
            self.button_long_pressed = True
            self.handle_button_press()


    def on_button_pressed(self) -> None:
        self.button_long_pressed = False


    def on_button_released(self) -> None:
        if not self.button_long_pressed:
            self.handle_button_press()
