import getpass
from typing import Any, Dict, Optional

import keyring


class Plugin:
    def __init__(self, notifier: Any, config: Dict[str, Any]):
        self._notifier = notifier
        self.invalid_key = None

        for key, value in config.items():
            if isinstance(value, dict) and value.get("password_secure"):
                if "password" in value or "password_base64" in value:
                    self.invalid_key = key
                    break

                config[key]["password"] = self.get_password(key.split("_")[0], value["user"])


    def validate(self, config: Dict[str, Any]) -> Optional[str]:
        if self.invalid_key:
            return "Credentials in \"{}\" cannot contain plain text or Base64 encoded password" \
                .format(self.invalid_key)

        return None


    def start(self) -> None:
        pass


    def stop(self) -> None:
        pass


    def get_password(self, credentials_name: str, username: str) -> str:
        service = "laundry_notifier_{}".format(credentials_name)
        password = keyring.get_password(service, username)

        if not password:
            password = getpass.getpass("Enter password for \"{}\" (user=\"{}\"): "
                .format(credentials_name, username))
            keyring.set_password(service, username, password)

        return password
