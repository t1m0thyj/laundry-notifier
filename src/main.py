import logging
import json
import os.path

from notifier import LaundryNotifier


def main():
    cwd = os.path.dirname(__file__)
    with open(os.path.join(cwd, "..", "config.json"), 'r') as fileobj:
        config = json.load(fileobj)
    logging.basicConfig(level=getattr(logging, config["log_level"].upper()))

    notifier = LaundryNotifier(config)
    try:
        notifier.start()
    except (KeyboardInterrupt, SystemExit):
        notifier.stop()


if __name__ == "__main__":
    main()
