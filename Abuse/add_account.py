# Add a new user account from CLI
import account
import twitch
from utility import accounts


def verify_account(username, password):
    """
    Verify the username and password are from a valid Twitch account
        username,password - Username and password pair : String
        username,password -> Bool
    """
    print("[*] Verifying twitch account")
    # Create temporary account with associated username,password
    temp_account = account.Account(username)
    temp_account.create(password, temporary=True)

    # Verify through Twitch login
    twitch_page = twitch.Twitch(temp_account)
    return twitch_page.run()


def verify_phone_number(phone_number):
    """
    Verify phone_number is a valid phone number
        phone_number - Phone number to verify : String
        phone_number -> Bool
    """
    print("[*] Verifying phone number")
    import phonenumbers  # importing previously imported modules has little to no overhead - safer to import here as some may not use twilio/phonenumbers

    try:
        number = phonenumbers.parse(phone_number)
    except:
        return False

    return phonenumbers.is_valid_number(number)


def add_account(user_info=None):
    """
    Create a new account all user info is verified before saving - May be called from CLI
        user_info - [username, password, is_admin, phone_number] Only required fields are username and password: Array
    """
    if user_info == None:
        user_info = []

        print("Username: ")
        user_info.append(input(">> "))
        print("Password: ")
        user_info.append(input(">> "))
        print("Are they an admin (True/False)(May be left empty): ")
        user_info.append(True if input(">> ").lower().strip()
                         == "true" else False)
        print("Phone number (May be left empty):")
        user_info.append(input(">> "))

        if user_info[3] != "":
            if not verify_phone_number(user_info[3]):
                print("[!!] Phone number is not valid")
                raise SystemExit

    else:
        if len(user_info) > 4:
            print("[!!] Too much user information")
            raise SystemExit

        elif len(user_info) > 3:
            if not verify_phone_number(user_info[3]):
                print("[!!] Phone number is not valid")
                raise SystemExit

        elif len(user_info) > 2:
            user_info[2] = (True if user_info[2].lower().strip()
                            == "true" else False)

    # Update user account
    if any(person.username == user_info[0] for person in accounts.get_accounts()):
        print("[+] updating exsisting account: %s " % user_info[0])
        user = account.Account(user_info[0])
        user.load()
        user.create(*user_info[1:])

    # Create user account
    elif verify_account(user_info[0], user_info[1]):
        user = account.Account(user_info[0])
        user.create(*user_info[1:])
        print("[+] Account creation successful")

    else:
        print("[!!] Twitch account credentials are not valid")
        raise SystemExit


if __name__ == "__main__":
    import sys

    # Check for args
    if len(sys.argv) > 2:
        add_account(sys.argv[1:])
    else:
        add_account()
