import logging
import random
import threading
import time
from typing import Any, Dict, Optional

from Adafruit_SSD1306 import SSD1306_128_32  # pylint: disable=import-error
from PIL import Image, ImageDraw, ImageFont


class AdafruitI2CFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return not "Adafruit_I2C" in record.getMessage() or record.levelno > logging.INFO


class Plugin:
    def __init__(self, notifier: Any, config: Dict[str, Any]):
        self._notifier = notifier
        for handler in logging.getLogger().handlers:
            handler.addFilter(AdafruitI2CFilter())
        self.display = SSD1306_128_32(None)


    def validate(self, config: Dict[str, Any]) -> Optional[str]:
        if len(config.get("machines", [])) != 2:
            return "Exactly two machines required in config.json"

        if not config.get("users"):
            return "At least one user required in config.json"

        if len([user for user in config["users"] if user.get("notify_machines")]) > 1:
            return "Only one user can have notify_machines listed in config.json"

        return None


    def start(self) -> None:
        self.display.begin()
        threading.Thread(target=self.update_display).start()


    def stop(self) -> None:
        self.display.clear()
        self.display.display()


    def get_machine_status(self, id: int) -> str:
        status_str = "OFF"
        if self._notifier.machines[id].is_on:
            status_str = self._notifier.machines[id].get_running_time_str()
        return "{}: {}".format(self._notifier.machines[id].name, status_str)


    def get_notify_status(self) -> str:
        status_str = "OFF"
        for user in self._notifier.users:
            if user.notify_machines:
                status_str = user.name
                break
        return "Notify: {}".format(status_str)


    def update_display(self) -> None:
        last_reposition_time = -1  # type: float
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
            draw.text((x_pos, y_pos + 16), self.get_notify_status(), fill=255, font=font)
            self.display.image(image)
            self.display.display()
            time.sleep(0.1)
