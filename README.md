# Twitch Drops

A set of OOP python programs to automatically claim Smite Game drops through twitch automatically.\
Allows for multiple accounts to be processed simultaneously with persistant storage of cookies annd notfications on completion as well as individual drops via text message.

## Installation

1. Install the latest stable version of [python3](https://www.python.org/downloads/).
2. Install the remaining packages in requirements and setup the file structure by running `install_requirements.py`:

   ```bash
   python install_requirements.py
   ```

3. Install the latest stable version of the selenium [chrome webdriver](https://chromedriver.chromium.org/downloads) and place it in `Abuse\resources\webdrivers`.
4. (Optional) If you have notifcations set on then on first run you will be prompted for your twilio information which can be set up at https://www.twilio.com/try-twilio.

## Usage

1. First add a user account for each user.
   ```bash
   python add_account.py
   # OR
   python add_account.py 'username' 'password' 'is_admin(True/False)' 'phone number'
   ```
2. Change the flags in `Abuse\main.py Line:13-17` if you want the twitch tabs to not be shown, you want to turn auto claim off or you want to turn notifications off.
3. WARNING if you do not have Twilio then turn notifcations off.
4. Run for all stored users.
   ```bash
   python main.py
   ```

## License

me no know

## Todo

- Bug fixes
    - Accept mature audience streams
    - Do something with Amazon watch party streams, stems from some streamers not correctly categorising their streams
    - Possible bug when checking if there are any redeemable rewards left
- Add a GUI
