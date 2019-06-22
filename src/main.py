import logging
import json
import os.path

from notifier_pioled import PiOLEDLaundryNotifier


def main():
    cwd = os.path.dirname(__file__)
    with open(os.path.join(cwd, "..", "config.json"), 'r') as fileobj:
        config = json.load(fileobj)
    logging.basicConfig(level=getattr(logging, config.get("log_level", "info").upper()))

    notifier = PiOLEDLaundryNotifier(config)
    try:
        notifier.start()
    except (KeyboardInterrupt, SystemExit):
        notifier.stop()


if __name__ == "__main__":
    main()
