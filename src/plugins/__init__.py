def load(name, notifier, config):
    return __import__(name).Plugin(notifier, config)
