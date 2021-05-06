# Defines notifier class and deals with all sending messages
from twilio.rest import Client
from tell_me_done import data_interface
from utility import accounts
import account


class Notifier:
    """
    Class that deals with sending messages and initialising recivier
        receive - Will the user be receiving messages : Boolean
        done_message - Message to send when done : String
        var_message - Message to send when new vars required : String
    """

    def __init__(self, receive=False, done_message="Simulation finished!", var_message="Program requires some variables!"):
        data_json = data_interface.get_keys()
        self.twilio_number = data_json['TWILIO_PHONE_NUMBER']
        self.done_message = done_message
        self.var_message = var_message
        self.client = Client(
            data_json['TWILIO_ACCOUNT_SID'], data_json['TWILIO_AUTH_TOKEN'])

    def notify(self, message=None, admin_only=False, done=False, need_vars=False):
        """
        Broadcast a message to a set of users based on the paramaters
            message - Message to send : String
            admin_only - Should the message only go to admins : Boolean
            done - Should the done message be sent : Boolean
            need_vars - Should the var message be sent : Boolean
            message, admin_only, done, need_vars -> Boolean
        """
        if message is not None:
            pass
        elif done:
            message = self.done_message
        elif need_vars:
            message = self.var_message
        else:
            print("[!] A message is required")
            return False

        users = accounts.get_accounts()

        if not users:
            print("[!] No users matched")
            return False

        for user in users:
            if not admin_only or (admin_only and user.admin):
                self.send(message, user=user)

        return True

    def send(self, message, phone_number=None, user=None):
        """
        Send a message to a specific phone_number/user, at least one must be specified
            message - Message to send : String
            phone_number - The phone number to send to : String
            user - The user object to send to : Account
            message, phone_number, user -> Boolean
        """
        if user == None and phone_number == None:
            print("[!] Must specify one")
            return False

        if user is None:
            users = accounts.get_accounts()

            for user_account in users:
                if user_account.phone_number == phone_number:
                    user = user_account
                    break

        if user is None:
            print("[!] No users match this number")
            return False

        print("<< Message sent to %s" %
              (user.username if user.username is not None else user.phone))
        if user.username is not None:
            message = user.username + " " + message

        self.client.messages.create(body=message,
                                    from_=self.twilio_number,
                                    to=user.phone
                                    )

        return True
