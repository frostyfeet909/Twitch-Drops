# Functionallity for working with groups of Account's
import os
import account
from os import path


def get_accounts():
    """
    Return all created accounts.
        accounts - Collection of account objects : Array
        -> accounts
    """
    accounts = []
    folder = path.join(path.dirname(path.realpath(__file__)),
                       "..", "resources", "users")

    if not path.isdir(folder):
        print("[!!] No users")
        raise FileNotFoundError

    folder = os.listdir(folder)

    if not folder:
        print("[*] No users")
        return []

    for account_name in folder:
        try:
            username = account_name.removesuffix(".json")
        except AttributeError:
            print("[!] Python version does not support removesuffix - be careful")
            username = account_name[:-5]

        user = account.Account(username)
        user.load()
        accounts.append(user)

    return accounts
