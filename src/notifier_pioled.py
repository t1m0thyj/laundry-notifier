import logging
import random
import threading
import time

import adafruit_ssd1306
import busio
from board import SCL, SDA
from gpiozero import DigitalInputDevice
from PIL import Image, ImageDraw, ImageFont

from notifier import LaundryNotifier


class PiOLEDLaundryNotifier(LaundryNotifier):
    def __init__(self, *args):
        super().__init__(*args)
        self.button = DigitalInputDevice(5, pull_up=True, bounce_time=0.1)
        i2c = busio.I2C(SCL, SDA)
        self.display = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)


    def start(self):
        LaundryNotifier.start(self)
        self.read_button_input()
        self.button.when_deactivated = self.on_button_up
        threading.Thread(target=self.update_display).start()


    def stop(self):
        LaundryNotifier.stop(self)
        self.button.when_deactivated = None
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


    def on_button_up(self):
        self.read_button_input(self.button.active_time > 0.5)


    def read_button_input(self, turn_off=False):
        if turn_off:
            self.users[0].should_notify = False
            self.users[1].should_notify = False
        elif self.users[0].should_notify:
            self.users[0].should_notify = False
            self.users[1].should_notify = True
        else:
            self.users[0].should_notify = True
            self.users[1].should_notify = False

        logging.info(self.get_notify_status())


    def update_display(self):
        last_reposition_time = -1
        x_pos, y_pos = 0, 0
        width, height = self.display.width, self.display.height
        font = ImageFont.load_default()

        while not self.should_stop:
            current_time = time.time()
            if (current_time - last_reposition_time) > 3600:
                last_reposition_time = current_time
                x_pos = random.randint(0, 44)
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

