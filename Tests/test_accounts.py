import os
from os import path
import subprocess
import pytest


@pytest.fixture(autouse=True)
def change_cwd():
    os.chdir("Abuse")
    yield
    os.chdir('..')


class TestAddingAccount:
    """
    Test adding account
        username,password - Valid Twitch username password combination : String
        phone - Valid phone number : String
        info - username,password : Array
    """
    username = ''
    password = ''
    phone = ""
    info = [username, password]

    def remove_account(self, username=None):
        if username == None:
            username = self.username

        if path.isfile('resources/users/%s.json' % username):
            os.remove('resources/users/%s.json' % username)

    def add_account(self, info=None):
        if info == None:
            info = self.info

        args = ["python", "add_account.py"] + info
        print(args)
        subprocess.run(args)

    def test_normal(self):
        self.remove_account()
        self.add_account()
        assert path.isfile('resources/users/%s.json' % self.username)

    def test_erroneous(self):
        username = 'peter pan'
        password = 'magic mushrooms'
        info = [username, password]
        self.add_account(info)
        assert not path.isfile('resources/users/%s.json' % username)

    def test_extreme(self):
        # Skips account verificationn from test_normal
        admin = 'True'
        info = self.info + [admin, self.phone]
        self.add_account(info)
        assert path.isfile('resources/users/%s.json' % self.username)
