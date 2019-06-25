import os.path
import sys

sys.path.append(os.path.dirname(__file__))


def load(name, notifier, config):
    return __import__(name).Plugin(notifier, config)
