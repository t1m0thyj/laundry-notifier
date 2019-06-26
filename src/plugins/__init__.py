import os.path
import sys
from typing import Any, Dict

sys.path.append(os.path.dirname(__file__))


def load(name: str, notifier: Any, config: Dict[str, Any]) -> Any:
    return __import__(name).Plugin(notifier, config)
