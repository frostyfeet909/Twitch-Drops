# Methods for saving and retrieving cookies
import json
from os import path


def save_cookies(cookies, file_loc):
    """
    Save cookies in the file_loc
        cookies - Cookies : dir
        file_loc - File to save cookies : String
        cookies, file_loc ->
    """
    with open(file_loc, 'w') as file:
        json.dump(cookies, file)


def load_cookies(file_loc):
    """
    Retrieve cookies from file_loc
        file_loc - File to save cookies : String
        file_loc -> cookies
    """

    # Verification file exsists
    if not path.isfile(file_loc):
        print("[!!] No cookies file")
        raise FileNotFoundError

    with open(file_loc, 'r') as file:
        cookies = json.load(file)

    return cookies
