from gpiozero import Button

BUTTON_PIN = 5


class Plugin:
    def __init__(self, notifier, config):
        self._notifier = notifier
        self.button = Button(BUTTON_PIN, pull_up=True, bounce_time=0.1)
        self.button_long_pressed = False
        self.current_user = -1

        for i, user in enumerate(self._notifier.users):
            if user.notify_machines:
                self.current_user = i
                break


    def validate_config(self, config):
        if not config.get("users"):
            return "At least one user required in config.json"

        if len([user for user in config["users"] if user.get("notify_machines")]) > 1:
            return "Only one user can have notify_machines listed in config.json"


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


    def on_button_held(self):
        if len(self._notifier.users) > 1:
            self.button_long_pressed = True
            self.handle_button_press()


    def on_button_pressed(self):
        self.button_long_pressed = False


    def on_button_released(self):
        if not self.button_long_pressed:
            self.handle_button_press()
