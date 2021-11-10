# Stores account information persistantly
import json
import os
from os import path
import threading


class Account:
    # TODO : Use collections.UserDict ???
    """Models a user account.

    Stores username, password, phone number and cookies persistantly.

    Attributes:
        username : str - Unique for Twitch so acts as an ID
        admin : bool - Is the user an admin (for purposes of notifications)
        lock : Lock - Use when changing account details e.g. cookies
        _file_lock : Lock - Lock for saving and loading
        _temporary : bool - Is this user account temporary
    """

    _file = path.join(path.dirname(path.realpath(__file__)), "resources", "users")

    def __init__(self, username: str) -> None:
        self.username = username
        self.lock = threading.Lock()
        self.password = None
        self.phone = None
        self.admin = None
        self.cookies = None
        self._file_lock = threading.Lock()  # TODO : Simplify this
        self._temporary = False

    def _save(self) -> None:
        """Save the account."""
        if self._temporary:
            return

        # Format for json
        data = {
            "password": self.password,
            "phone": self.phone,
            "admin": self.admin,
            "cookies": self.cookies,
        }

        self._file_lock.acquire()
        with open(path.join(Account._file, self.username + ".json"), "w") as file:
            json.dump(data, file)
        self._file_lock.release()

    def delete(self) -> None:
        """Delete the account.

        Generally due to incorrect data.
        """
        if self._temporary:
            return

        if not path.isfile(path.join(Account._file, self.username + ".json")):
            print("[!!] %s does not exsist" % self.username)
            raise FileNotFoundError

        self._file_lock.acquire()
        os.remove(path.join(Account._file, self.username + ".json"))
        self._file_lock.release()

    def load(self) -> None:
        """Load the account from storage.

        Raises:
            FileNotFoundError - If the user account is not stored
        """
        if not path.isfile(path.join(Account._file, self.username + ".json")):
            print("[!!] %s does not exsist" % self.username)
            raise FileNotFoundError

        self._file_lock.acquire()
        with open(path.join(Account._file, self.username + ".json"), "r") as file:
            data = json.load(file)

        self.password = data["password"]
        self.phone = data["phone"]
        self.admin = data["admin"]
        self.cookies = data["cookies"]
        self._file_lock.release()

    def create(
        self,
        password: str = None,
        is_admin: bool = False,
        phone_number: str = None,
        temporary: bool = False,
    ) -> None:
        """Create a fresh account.

        May overwrite old account with same username.
        """
        self._temporary = temporary

        if password == "":
            password = None
        self.password = password

        if phone_number == "":
            phone_number = None
        self.phone = phone_number

        # Extra safe
        self.admin = is_admin == True or str(is_admin).strip().lower() == "true"

        self._save()

    def login(self, cookies: list[dir]) -> None:
        """Login account to Twitch.

        When you got cookies, who needs a password?
        """
        self.cookies = cookies
        self.password = None
        self._save()
