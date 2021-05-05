# Add a new user account from CMD
import account


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
        user_info.append(input(">> "))
        print("Phone number:")
        user_info.append(input(">> "))

    user = account.Account(user_info[0])
    user.create(*user_info[1:])


if __name__ == "__main__":
    import sys

    # Check for args
    if len(sys.argv) > 3:
        add_account(sys.argv[1:])
    else:
        add_account()
