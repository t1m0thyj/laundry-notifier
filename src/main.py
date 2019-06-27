import logging
import json
import os.path
import re
from typing import Any, IO

from notifier import LaundryNotifier


def load_json_with_comments(fileobj: IO[str]) -> Any:
    # Regex from https://github.com/sindresorhus/comment-regex
    comment_regex = re.compile(r"(?:(?:^|\s)//(.+?)$)|(?:/\*(.*?)\*/)",
        flags=re.MULTILINE | re.DOTALL)
    return json.loads(re.sub(comment_regex, r"", fileobj.read()))


def main() -> None:
    cwd = os.path.dirname(__file__)
    with open(os.path.join(cwd, "..", "config.json"), 'r') as fileobj:
        config = load_json_with_comments(fileobj)
    logging.basicConfig(level=getattr(logging, config["log_level"].upper()))

    notifier = LaundryNotifier(config)
    try:
        notifier.start()
    except (KeyboardInterrupt, SystemExit):
        notifier.stop()


if __name__ == "__main__":
    main()
