import logging

from gpiozero import Button

BUTTON_PIN = 5


class Plugin:
    def __init__(self, notifier, config):
        self._notifier = notifier
        self.button = Button(BUTTON_PIN, pull_up=True, bounce_time=0.1)
        self.button_long_pressed = False
        self.current_user = -1

        for i, user in enumerate(self._notifier.users):
            if user.should_notify:
                self.current_user = i
                break


    def validate_config(self, config):
        if not config.get("users"):
            return "There must be at least one user in config.json"

        if len(config["users"].filter(lambda user: user.get("notify"))) > 1:
            return "Only one user can have notify=true in config.json"


    def start(self):
        self.button.when_held = self.on_button_held
        self.button.when_pressed = self.on_button_pressed
        self.button.when_released = self.on_button_released


    def stop(self):
        self.button.when_held = None
        self.button.when_pressed = None
        self.button.when_released = None


    def handle_button_press(self):
        if self.button_long_pressed or (len(self._notifier.users) == 1 and
                self._notifier.users[0].should_notify):
            self.current_user = -1
        else:
            self.current_user += 1
            if self.current_user >= len(self._notifier.users):
                self.current_user = 0

        for i, user in enumerate(self._notifier.users):
            user.should_notify = i == self.current_user
        logging.info(self._notifier.get_notify_status())


    def on_button_held(self):
        if len(self._notifier.users) > 1:
            self.button_long_pressed = True
            self.handle_button_press()


    def on_button_pressed(self):
        self.button_long_pressed = False


    def on_button_released(self):
        if not self.button_long_pressed:
            self.handle_button_press()
