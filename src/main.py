import json
import logging
import os
import re
from logging.handlers import MemoryHandler, RotatingFileHandler
from typing import Any, IO

from notifier import LaundryNotifier


def load_json_with_comments(fileobj: IO[str]) -> Any:
    # Regex from https://github.com/sindresorhus/comment-regex
    comment_regex = re.compile(r"(?:(?:^|\s)//(.+?)$)|(?:/\*(.*?)\*/)",
        flags=re.MULTILINE | re.DOTALL)
    return json.loads(re.sub(comment_regex, r"", fileobj.read()))


def init_logger(logs_dir, log_level="info"):
    os.makedirs(logs_dir, exist_ok=True)
    file_handler = RotatingFileHandler(os.path.join(logs_dir, "app.log"), maxBytes=1024 * 1024, backupCount=10)
    memory_handler = MemoryHandler(1024 * 10, flushLevel=logging.ERROR, target=file_handler)
    logging.basicConfig(level=getattr(logging, log_level.upper()), handlers=[memory_handler, logging.StreamHandler()])


def main() -> None:
    cwd = os.path.dirname(__file__)
    with open(os.path.join(cwd, "..", "config.json"), 'r') as fileobj:
        config = load_json_with_comments(fileobj)
    init_logger(os.path.join(cwd, "..", "logs"), config["log_level"])

    notifier = LaundryNotifier(config)
    try:
        notifier.start()
    except (KeyboardInterrupt, SystemExit):
        notifier.stop()


if __name__ == "__main__":
    main()
