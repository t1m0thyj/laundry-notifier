from typing import Any, Dict, List, Optional

import MySQLdb

from credentials import Credentials
from machine import Machine
from notifier import LaundryNotifier
from user import User

USERDB_NAME = "LaundryNotifier"


class Plugin:
    def __init__(self, notifier: Any, config: Dict[str, Any]):
        self._notifier = notifier
        self.conn = None
        self.credentials = Credentials("userdb", config)
        self.db_name = config.get("userdb_name", USERDB_NAME)


    def validate(self, config: Dict[str, Any]) -> Optional[str]:
        if config.get("users"):
            return "No users can be listed in config.json"

        return None


    def start(self) -> None:
        self.conn = MySQLdb.connect(host=self.credentials.host, port=self.credentials.port,
            user=self.credentials.user, passwd=self.credentials.password, db=self.db_name)
        self._notifier.get_subscribed_users = self.get_subscribed_users


    def stop(self) -> None:
        self._notifier.get_subscribed_users = LaundryNotifier.get_subscribed_users
        self.conn.close()


    def get_subscribed_users(self, machine: Machine) -> List[User]:
        user_list = []
        self.conn.ping(True)

        with self.conn.cursor() as cur:
            cur.execute("SELECT * FROM TABLE_NAME")
            for row in cur.fetchall():
                user_list.append(User(self._notifier, row["Name"], row["Email"]))

        return user_list
