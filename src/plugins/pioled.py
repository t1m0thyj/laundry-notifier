import random
import threading
import time

from Adafruit_SSD1306 import SSD1306_128_32
from PIL import Image, ImageDraw, ImageFont


class Plugin:
    def __init__(self, notifier, config):
        self._notifier = notifier
        self.display = SSD1306_128_32(None)


    def validate_config(self, config):
        if len(config.get("machines", [])) != 2:
            return "There must be exactly two machines in config.json"

        if not config.get("users"):
            return "There must be at least one user in config.json"


    def start(self):
        self.display.begin()
        threading.Thread(target=self.update_display).start()


    def stop(self):
        self.display.clear()
        self.display.display()


    def get_machine_status(self, id):
        status_str = "OFF"
        if self._notifier.machines[id].is_on:
            status_str = self._notifier.machines[id].get_running_time_str()
        return "{}: {}".format(self._notifier.machines[id].name, status_str)


    def update_display(self):
        last_reposition_time = -1
        x_pos, y_pos = 0, 0
        width, height = self.display.width, self.display.height
        image = Image.new('1', (width, height))
        draw = ImageDraw.Draw(image)
        font = ImageFont.load_default()

        while not self._notifier.stopped:
            current_time = time.time()
            if (current_time - last_reposition_time) > 3600:
                last_reposition_time = current_time
                x_pos = random.randint(0, 31)
                y_pos = random.randint(-2, 7)

            draw.rectangle((0, 0, width, height), fill=0, outline=0)
            draw.text((x_pos, y_pos), self.get_machine_status(0), fill=255, font=font)
            draw.text((x_pos, y_pos + 8), self.get_machine_status(1), fill=255, font=font)
            draw.text((x_pos, y_pos + 16), self._notifier.get_notify_status(), fill=255, font=font)
            self.display.image(image)
            self.display.display()
            time.sleep(0.1)
