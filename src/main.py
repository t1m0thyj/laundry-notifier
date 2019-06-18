import logging
import json
import os.path

from notifier_pioled import PiOLEDLaundryNotifier


def main():
    logging.basicConfig(level=logging.DEBUG)
    cwd = os.path.dirname(__file__)
    with open(os.path.join(cwd, "..", "config.json"), 'r') as fileobj:
        config = json.load(fileobj)
    PiOLEDLaundryNotifier(config).start()


if __name__ == "__main__":
    main()
