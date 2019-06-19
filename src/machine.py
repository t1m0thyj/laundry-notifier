import logging
import re
import time
from datetime import timedelta

import gpiozero

MAX_OFF_TIME = "max_off_time"
MIN_ON_TIME = "min_on_time"
NOTIFY_DELAY = "notify_delay"


class Machine:
    def __init__(self, adc_model, name, adc_channel, adc_threshold, time_args=None):
        self.name = name
        self.adc = getattr(gpiozero, adc_model)(adc_channel)
        self.adc_threshold = adc_threshold
        self.time_args = time_args if time_args is not None else {}

        self.adc_on = False
        self.adc_values = []
        self.is_on = False
        self.last_state_change_time = -1
        self.started_time = -1


    def get_running_time(self):
        time_str = str(timedelta(seconds=time.time() - self.started_time))
        return re.sub(r"^0:|\.\d+$", r"", time_str)


    def update(self):
        self.adc_values.append(self.adc.value * 3.3)
        if len(self.adc_values) > 10:
            self.adc_values.pop(0)
        adc_value_range = (max(self.adc_values) - min(self.adc_values)) if len(self.adc_values) == 10 else 0
        logging.debug("[{}] {}".format(self.name, round(adc_value_range, 3)))

        adc_on = adc_value_range > self.adc_threshold
        current_time = time.time()
        if adc_on != self.adc_on:
            self.last_state_change_time = current_time
        self.adc_on = adc_on
        is_on = self.is_on

        if adc_on and (not self.is_on) and (current_time - self.last_state_change_time) > 1:
            is_on = True
            self.started_time = current_time
        elif (not adc_on) and self.is_on and (current_time - self.last_state_change_time) > 1:
            finish_allowed = True

            if (MIN_ON_TIME in self.time_args and
                    (current_time - self.started_time) < self.time_args[MIN_ON_TIME]):
                if (MAX_OFF_TIME not in self.time_args or
                        (current_time - self.last_state_change_time) <
                        self.time_args[MAX_OFF_TIME]):
                    finish_allowed = False

            if (NOTIFY_DELAY in self.time_args and
                    (current_time - self.last_state_change_time) < self.time_args[NOTIFY_DELAY]):
                finish_allowed = False

            if finish_allowed:
                is_on = False

        status_changed = is_on != self.is_on
        self.is_on = is_on
        return status_changed
