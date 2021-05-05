# Reading/Saving twilio info
from os.path import join, dirname, realpath, isfile, isdir
from os import mkdir
from json import load as json_load
from json import dump as json_dump
from getpass import getpass
import threading

# Make threading safe
lock = threading.Lock()


def request_keys(account_SID=True, auth_token=True, phone_number=True):
    """
    Request and Store twilio info safley
        account_SID - Twilio account SID not already saved: Bool
        auth_token - Twilio authentication token not already saved : Bool
        phone_number - Twilio phone number not already saved : Bool
        password - Admin password for users not already saved : Bool
    """
    print("[!] Twilio account details required!")
    print("\n")

    if account_SID:
        print("Twilio account SID:")
        account_SID = input(">> ")

    if auth_token:
        print("Twilio authentication token:")
        auth_token = getpass(prompt='>> ')

    if phone_number:
        print("Twili phone number:")
        phone_number = input(">> ")

    save_keys(account_SID, auth_token, phone_number)


def check_dir(path):
    """
    Check there's a resources folder, run on user visible functions and those run from Notifier
        path - Base dir : String
    """
    if not isdir(join(path, "resources")):
        mkdir(join(path, "resources"))


def get_keys():
    """
    Get Twilio info from json file
        data - Twilio info : dir
        -> data
    """
    path = dirname(realpath(__file__))
    check_dir(path)

    if not isfile(join(path, "resources", "keys.json")):
        request_keys()

    lock.acquire()
    with open(join(path, "resources", "keys.json"), "r") as file:
        data = json_load(file)
    lock.release()

    if any(item == "" for item in data.values()):
        request_keys()

        lock.acquire()
        with open(join(path, "resources", "keys.json"), "r") as file:
            data = json_load(file)
        lock.release()

    return data


def save_keys(account_SID, auth_token, phone_number):
    """
    Save Twilio info from json file
        account_SID - Twilio account SID: String
        auth_token - Twilio authentication token : String
        phone_number - Twilio phone number : String
        account_SID, auth_token, phone_number, password -> 
    """
    path = dirname(realpath(__file__))

    # Format to save json data
    data = {"TWILIO_ACCOUNT_SID": account_SID,
            "TWILIO_AUTH_TOKEN": auth_token, "TWILIO_PHONE_NUMBER": phone_number}

    lock.acquire()
    with open(join(path, "resources", "keys.json"), "a") as file:
        json_dump(data, file)
    lock.release()
