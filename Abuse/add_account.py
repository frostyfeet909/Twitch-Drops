# Add a new user account from CMD
import account
import twitch
import phonenumbers
from utility import accounts


def verify_account(username, password):
    print("[*] Verifying twitch account")
    temp_account = account.Account(username)
    temp_account.create(password, temporary=True)

    twitch_page = twitch.Twitch(temp_account)
    return twitch_page.run()


def verify_phone_number(phone_number):
    print("[*] Verifying phone number")
    try:
        number = phonenumbers.parse(phone_number)
    except:
        return False

    return phonenumbers.is_valid_number(number)


def add_account(user_info=None):
    """
    Create a new account - May be called from CMD
        user_info - [username, password, is_admin, phone_number] : Array
    """
    if user_info == None:
        user_info = []

        print("Username: ")
        user_info.append(input(">> "))
        print("Password: ")
        user_info.append(input(">> "))
        print("Are they an admin (True/False): ")
        user_info.append(True if input(">> ").lower().strip()
                         == "true" else False)
        print("Phone number:")
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

    if any(person.username == user_info[0] for person in accounts.get_accounts()):
        print("[+] updating exsisting account: %s " % user_info[0])
        user = account.Account(user_info[0])
        user.load()
        if len(user_info) > 2:
            user.admin = user_info[2]
            if len(user_info) > 3:
                user.phone = user_info[3]

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
