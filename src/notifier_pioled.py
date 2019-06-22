import logging
import random
import threading
import time

from ..adafruit_ssd1306 import SSD1306_128_32
from gpiozero import Button
from PIL import Image, ImageDraw, ImageFont

from notifier import LaundryNotifier

BUTTON_PIN = 5
DISPLAY_RESET_PIN = 24


class PiOLEDLaundryNotifier(LaundryNotifier):
    def __init__(self, *args):
        super().__init__(*args)
        self.validate_config()
        self.button = Button(BUTTON_PIN, pull_up=True, bounce_time=0.1)
        self.button_long_pressed = False
        self.display = SSD1306_128_32(DISPLAY_RESET_PIN)


    def start(self):
        LaundryNotifier.start(self)
        self.button.when_held = self.on_button_held
        self.button.when_pressed = self.on_button_pressed
        self.button.when_released = self.on_button_released
        threading.Thread(target=self.update_display).start()


    def stop(self):
        LaundryNotifier.stop(self)
        self.button.when_held = None
        self.button.when_pressed = None
        self.button.when_released = None
        self.display.fill(0)
        self.display.show()


    def get_machine_status(self, id):
        status_str = "OFF" if not self.machines[id].is_on else self.machines[id].get_running_time()
        return "{}: {}".format(self.machines[id].name, status_str)


    def get_notify_status(self):
        status_str = "OFF"
        if self.users[0].should_notify:
            status_str = self.users[0].name
        elif self.users[1].should_notify:
            status_str = self.users[1].name
        return "Notify: {}".format(status_str)


    def handle_button_press(self):
        if self.button_long_pressed:
            self.users[0].should_notify = False
            self.users[1].should_notify = False
        else:
            self.users[0].should_notify = not self.users[0].should_notify
            self.users[1].should_notify = not self.users[0].should_notify

        logging.info(self.get_notify_status())


    def on_button_held(self):
        self.button_long_pressed = True
        self.handle_button_press()


    def on_button_pressed(self):
        self.button_long_pressed = False


    def on_button_released(self):
        if not self.button_long_pressed:
            self.handle_button_press()


    def update_display(self):
        last_reposition_time = -1
        x_pos, y_pos = 0, 0
        width, height = self.display.width, self.display.height
        font = ImageFont.load_default()

        while not self.stop_event.is_set():
            current_time = time.time()
            if (current_time - last_reposition_time) > 3600:
                last_reposition_time = current_time
                x_pos = random.randint(0, 31)
                y_pos = random.randint(-2, 9)

            image = Image.new('1', (width, height))
            draw = ImageDraw.Draw(image)
            draw.rectangle((0, 0, width, height), fill=0, outline=0)
            draw.text((x_pos, y_pos), self.get_machine_status(0), fill=255, font=font)
            draw.text((x_pos, y_pos + 8), self.get_machine_status(1), fill=255, font=font)
            draw.text((x_pos, y_pos + 16), self.get_notify_status(), fill=255, font=font)
            self.display.image(image)
            self.display.show()
            time.sleep(0.1)


    def validate_config(self):
        error = None

        if len(self.machines) != 2:
            error = "There must be exactly 2 machines in config.json"
        elif len(self.users) != 2:
            error = "There must be exactly 2 users in config.json"
        elif self.users[0].should_notify and self.users[1].should_notify:
            error = "Only 1 user can have notify=true in config.json"

        if error:
            logging.error(error)
        else:
            logging.info(self.get_notify_status())

        assert error is None
