import os
from os import path
import subprocess
import sys
import importlib


def get_location():
    """
    Returns the absolute file path
    """
    return path.dirname(path.realpath(__file__))


def make_dirs():
    location = path.join(get_location(), "Abuse")

    if not path.isdir(location):
        print("Abuse not found")
        return False

    results = [path.join(location, "resources"), path.join(location, "resources", "users"), path.join(
        location, "resources", "webdrivers"), path.join(location, "resources", "logs")]
    for result in results:
        if not path.isdir(result):
            os.mkdir(result)
            print("Made: %s" % result)

    return True


def install_modules():
    try:
        with open("requirements.txt", "r") as file:
            lines = file.readlines()
    except FileNotFoundError:
        print("requirements.txt not found")
        return False

    for line in lines:
        line = line.strip()
        print("Importing: %s" % line)

        try:
            importlib.import_module(line)
        except ImportError:
            print("Attempting to install: %s" % line)
            try:
                subprocess.call([sys.executable, "-m", "pip", "install", line])
            except:
                print("Could not install: %s" % line)
            else:
                print("Installed: %s" % line)


def run():
    if make_dirs() and install_modules():
        print("Completed succesfully")
    else:
        print("Something went wrong")


if "__main__" == __name__:
    run()
