import base64
import logging
from typing import Any, Dict


class Credentials:
    def __init__(self, name: str, config: Dict[str, Any]):
        credentials = config["{}_credentials".format(name)]
        self.host = credentials["host"]
        self.port = credentials["port"]
        self.user = credentials["user"]
        self.password = credentials["password"]

        if credentials.get("password_base64"):
            self.password = base64.b64decode(self.password).decode()
