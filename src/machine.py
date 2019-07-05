import logging
import time
from datetime import timedelta
from typing import Any, Dict, List, Optional

import gpiozero  # pylint: disable=import-error

OFF_DELAY_LENGTH = "off_delay_length"
OFF_DELAY_START = "off_delay_start"
OFF_DELAY_STOP = "off_delay_stop"
ON_DELAY_LENGTH = "on_delay_length"


class Machine:
    def __init__(self, adc_data: List[Dict[str, Any]], name: str, adc_channel: List[int],
            adc_threshold: float, time_args: Optional[Dict[str, int]]=None):
        self.name = name
        self.adc_threshold = adc_threshold
        self.time_args = time_args or {}

        adc_num, adc_channel_num = adc_channel
        adc_model = adc_data[adc_num]["model"].upper()
        adc_kwargs = adc_data[adc_num].get("gpio_args", {})
        self.adc = getattr(gpiozero, adc_model)(adc_channel_num, **adc_kwargs)

        self.adc_on = False
        self.adc_values = []  # type: List[float]
        self.is_on = False
        self.last_state_change_time = -1  # type: float
        self.started_time = -1  # type: float


    def get_running_time_str(self) -> str:
        time_str = str(timedelta(seconds=time.time() - self.started_time))

        if time_str.startswith("0:"):
            time_str = time_str[2:]

        return time_str.split(".", 2)[0]


    def is_off_allowed(self, current_time: float) -> bool:
        off_allowed = True
        off_delay_length = self.time_args.get(OFF_DELAY_LENGTH, -1)
        off_delay_start = self.time_args.get(OFF_DELAY_START, -1)
        off_delay_stop = self.time_args.get(OFF_DELAY_STOP, -1)

        if (off_delay_length != -1 and
                (current_time - self.last_state_change_time) < off_delay_length):
            if (not (off_delay_start != -1 and (current_time - self.started_time) <
                    off_delay_start) and not (off_delay_stop != -1 and
                    (current_time - self.started_time) > off_delay_stop)):
                off_allowed = False

        return off_allowed


    def is_on_allowed(self, current_time: float) -> bool:
        on_delay_length = self.time_args.get(ON_DELAY_LENGTH, -1)
        return (on_delay_length == -1 or
            (current_time - self.last_state_change_time) > on_delay_length)


    def read_adc_value_range(self) -> float:
        self.adc_values.append(self.adc.value * 3.3)
        if len(self.adc_values) > 10:
            self.adc_values.pop(0)

        adc_value_range = 0  # type: float
        if len(self.adc_values) == 10:
            adc_value_range = max(self.adc_values) - min(self.adc_values)
            logging.debug("[{}] {}".format(self.name, round(adc_value_range, 3)))

        return adc_value_range


    def update(self) -> bool:
        adc_on = self.read_adc_value_range() > self.adc_threshold
        current_time = time.time()
        if adc_on != self.adc_on:
            self.last_state_change_time = current_time
        self.adc_on = adc_on
        is_on = self.is_on

        if (current_time - self.last_state_change_time) > 1:
            if adc_on and (not self.is_on) and self.is_on_allowed(current_time):
                is_on = True
                self.started_time = current_time - self.time_args.get(ON_DELAY_LENGTH, 0)
            elif (not adc_on) and self.is_on and self.is_off_allowed(current_time):
                is_on = False

        status_changed = is_on != self.is_on
        self.is_on = is_on
        return status_changed
