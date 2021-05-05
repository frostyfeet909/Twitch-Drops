# Stores account information persistantly
import json
import threading
from os import path


class Account:
    """
    Models a user account that stores username, password, phone number and cookies persistantly
        username - Unique for Twitch so acts as an ID : String
    """
    file = path.join(path.dirname(path.realpath(__file__)),
                     "resources", "users")

    def __init__(self, username):
        self.username = username
        self.lock = threading.Lock()
        self.__file_lock = threading.Lock()  # Simplify this
        self.password = None
        self.phone = None
        self.admin = None
        self.cookies = None

    def __save(self):
        """
        Save the account
        """
        # Format for json
        data = {"password": self.password, "phone": self.phone,
                "admin": self.admin, "cookies": self.cookies}

        self.__file_lock.acquire()
        with open(path.join(Account.file, self.username+".json"), "w") as file:
            json.dump(data, file)
        self.__file_lock.release()

    def load(self):
        """
        Load the account from storage
        """
        if not path.isfile(path.join(Account.file, self.username+".json")):
            print("[!] %s does not exsist" % self.username)
            raise FileNotFoundError

        self.__file_lock.acquire()
        with open(path.join(Account.file, self.username+".json"), "r") as file:
            data = json.load(file)

        self.password = data["password"]
        self.phone = data["phone"]
        self.admin = data["admin"]
        self.cookies = data["cookies"]
        self.__file_lock.release()

    def create(self, password,  is_admin, phone_number=None):
        """
        Create a fresh account (or overwrite old account with same username)
        """
        self.password = password

        if phone_number == "":
            phone_number = None
        self.phone = phone_number

        self.admin = is_admin
        self.__save()

    def login(self, cookies):
        """
        Login account to Twitch - password is no longer needed
        """
        self.cookies = cookies
        self.password = None
        self.__save()
