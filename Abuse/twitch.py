# Objects to model Twitch screens
import os
from os import path
import platform
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common import action_chains
from selenium.webdriver.common import keys
from selenium.webdriver.chrome import options
from selenium.common.exceptions import NoSuchElementException
import threading
import account
from utility import time_lock


class Twitch(threading.Thread):
    """
    Base class for other windows, models a Twitch page with various functions
        username,password : String
        headless - Should selenium start headless if possible : Boolean
    """

    def __init__(self, user, headless=True):
        threading.Thread.__init__(self)
        self.driver = None
        self.url = None
        # Make sure interaction has at least 2 second timeout
        self.lock = time_lock.Time_Lock()
        self.user = user
        self.headless = headless
        self.active = True

    def setup(self):
        """
            Setup Twitch page - login and setup selenium webdriver
        """
        # If headless required, must ensure cookies exsist
        if self.user.cookies == None and self.headless:
            need_login = True
        else:
            need_login = False

        self.__setup_webdriver(need_login)

        # Check successful login
        if not self._login():
            print(self.user.username, "-", "[!!] Could not login.")
            raise PermissionError

        if need_login:
            self.__setup_webdriver(False)

    def run(self):
        """
        """
        return None

    def __setup_webdriver(self, cannot_headless):
        """
        Setup selenium webdriver
            cannot_headless - Cannot be headless if manual login is required : Bool
        """

        if self.driver != None:
            self.drier.quit()

        # Find webdriver
        plat = platform.platform().lower()

        # Webdriver stored differently on OS's
        if plat.startswith("win"):
            file_loc = path.join(path.dirname(path.realpath(
                __file__)), "resources", "webdrivers", "chromedriver.exe")
        elif plat.startswith("lin"):
            file_loc = '/usr/lib/chromium-browser/chromedriver'
        else:
            print(self.user.username, "-",
                  "[!!] Platform not supported.")
            raise EnvironmentError

        if not path.isfile(file_loc):
            print(self.user.username, "-",
                  "[!!] Chromium webdriver does not exsist!")
            raise FileNotFoundError

        # Setup webdriver
        chrome_options = options.Options()
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-gpu")

        # Need not headless for login
        if not cannot_headless and self.headless:
            chrome_options.add_argument("--headless")
        elif self.headless:
            print(self.user.username, "-",
                  "[!] No cookie file - must login manually.")

        self.driver = webdriver.Chrome(
            executable_path=file_loc, chrome_options=chrome_options)
        # self.driver.implicitly_wait(2)  # Don't think works

    def _login(self):
        """
        Login to Twitch
            -> Bool
        """
        if self.user.cookies == None:
            self.user.lock.acquire()
            self.user.load()

            if self.user.cookies != None:
                print("I founnd cookies?")
                self.user.lock.release()
                self.__login_by_cookies()
            else:
                print("Proper logging")
                self.__login_by_twitch()
                self.user.lock.release()
        else:
            self.__login_by_cookies()

        return True

    def __login_by_twitch(self):
        """
        Login to Twitch through Twitch login page
            -> Bool
        """
        self.lock.acquire()
        self.driver.get("https://www.twitch.tv/login")
        self.lock.release()

        # Enter username
        username_element = self.driver.find_element_by_id("login-username")
        self.lock.acquire()
        username_element.send_keys(self.user.username)
        self.lock.release()

        # Enter password
        password_element = self.driver.find_element_by_id("password-input")
        self.lock.acquire()
        password_element.send_keys(self.user.password)
        password_element.send_keys(keys.Keys.RETURN)
        self.lock.release()

        # Checks for various steps
        while self.__check_auth():
            print(self.user.username, "-",
                  "[!] Auth verification required.")
            time.sleep(10)

        while self.__check_not_robot():
            print(self.user.username, "-",
                  "[!] Robot verification required.")
            time.sleep(10)

        while self.__check_need_verify():
            print(self.user.username, "-",
                  "[!] New login verification required.")
            time.sleep(10)

        self.user.login(self.driver.get_cookies())
        return True

    def __login_by_cookies(self):
        """
        Login to Twitch by using cookies stored in the account
            -> Bool
        """
        self.lock.acquire()
        self.driver.get("https://www.twitch.tv")
        self.lock.release()

        cookies = self.user.cookies

        try:
            for cookie in cookies:
                self.driver.add_cookie(cookie)
        except:
            print("[!!] Cookie error.")
            raise ConnectionError

        self.lock.acquire()
        self.driver.refresh()
        self.lock.release()
        return True

    def __check_need_verify(self):
        """
        Check need to verify new login
            -> Bool
        """
        if self._find_element_xpath("//h4[contains(text(), 'Verify')]") != None:
            return True

        return False

    def __check_auth(self):
        """
        Check need to enter user authentication
            -> Bool
        """
        if self._find_element_xpath("//label[contains(text(), 'Token')]") != None:
            return True

        return False

    def __check_not_robot(self):
        """
        Check need to verify not a robot :3
            -> Bool
        """
        for _ in range(0, 2):
            try:
                self.driver.find_element_by_id('FunCaptcha')
                return True
            except NoSuchElementException:
                time.sleep(5)

        return False

    def _find_element_xpath(self, xpath):
        """
        Find and return element by xpath
            xpath - xpath of element : String
            element - Found element : Element?
            xpath -> element
        """
        # Try and wait twice - maybe slow connection or ad etc.
        for _ in range(0, 2):
            try:
                element = self.driver.find_element_by_xpath(xpath)
                return element
            except NoSuchElementException:
                time.sleep(5)

        return None

    def _click_element_xpath(self, xpath):
        """
        Find and click element by xpath
            xpath - xpath of element : String
            xpath -> Bool
        """
        element = self._find_element_xpath(xpath)

        if element != None:
            self.lock.acquire()
            element.click()
            self.lock.release()
            return True

        return False


class Stream(Twitch):
    """
    Models a Twitch stream page, found through a game directory page. with various functions
        user : Account
        drops_available - Are drops still available, indefinite execution if empty : Event
        headless - Should selenium start headless if possible : Boolean
        chat_on - Should chat be left on : Boolean
    """

    def __init__(self, user, drops_available=None, headless=True, chat_on=False):
        Twitch.__init__(self, user, headless)
        self.drops = drops_available
        # URL for directory of droppable streams
        self.url = "https://www.twitch.tv/directory/game/SMITE/tags/c2542d6d-cd10-4532-919b-3d19f30a768b"
        self.chat = chat_on

    def run(self):
        """
        Automate finding and watching droppable streams
        """
        self.setup()
        print(self.user.username, "-", datetime.now().strftime("%H:%M:%S"), "-",
              "[*] Stream Starting.")

        while (not self.drops.is_set() if self.drops != None else True):
            if not self._check_stream_alive():
                if self._find_stream():
                    self._optimise_stream()
            else:
                print(self.user.username, "-",
                      datetime.now().strftime("%H:%M:%S"), "-", "[*] Stream Running.")
                if self.chat:
                    self._claim_channel_points()

            time.sleep(600)

        print(self.user.username, "-", datetime.now().strftime("%H:%M:%S"),
              "-", "[*] Quitting stream.")
        self.driver.quit()

    def _optimise_stream(self):
        """
        Optimise current stream to lower resources
        """
        self.__mute()
        self.__lower_quality()

        if not self.chat:
            self.__close_chat()

    def _find_stream(self):
        """
        Find and goto a new stream
            -> Bool
        """
        self.lock.acquire()
        self.driver.get(self.url)
        self.lock.release()

        # Click on first valid stream
        if not self._click_element_xpath("//div[@data-target='directory-first-item']//a[@data-a-target='preview-card-title-link']"):
            print(self.user.username, "-", datetime.now().strftime("%H:%M:%S"), "-",
                  "[!] New stream not found.")
            return False

        print(self.user.username, "-", datetime.now().strftime("%H:%M:%S"), "-",
              "[*] New stream found.")
        print("    - %s" % self.driver.current_url)
        return True

    def _check_stream_alive(self):
        """
        Check if current stream is still live
            -> Bool
        """
        if not self._find_element_xpath("//div[@class='channel-info-content']//p[contains(text(), 'LIVE')]"):
            print(self.user.username, "-", datetime.now().strftime("%H:%M:%S"), "-",
                  "[!] Stream offline.")
            return False

        return True

    def _claim_channel_points(self):
        """
        Claim channel points
        """
        self._click_element_xpath(
            "//div[@class='claimable-bonus__icon tw-flex']")

    def __mute(self):
        """
        Mute stream
        """
        mute = action_chains.ActionChains(self.driver)
        mute.send_keys("m")
        self.lock.acquire()
        mute.perform()
        self.lock.release()

    def __lower_quality(self, quality=None):
        """
        Lower quality of stream to quality otherwise lowest option
            quality - Desired quality : String
        """
        # Menu button
        self._click_element_xpath(
            "//button[@data-a-target='player-settings-button']")

        # Dropdown button
        self._click_element_xpath(
            "//button[@data-a-target='player-settings-menu-item-quality']")

        # Trying lowest quality buttons
        if quality == None:
            for quality_setting in ['160p', '360p', '480p', '720p', 'Auto']:
                if self._click_element_xpath("//div[@data-a-target='player-settings-submenu-quality-option']//div[contains(text(), '%s')]" % quality_setting):
                    break
        else:
            self._click_element_xpath(
                "//div[@data-a-target='player-settings-submenu-quality-option']//div[contains(text(), '%s')]" % quality)

    def __close_chat(self):
        """
        Close stream chat
        """
        self._click_element_xpath(
            "//div[@data-test-selector='right-column-content__toggle'][contains(@class, 'expanded')]")


class Inventory(Twitch):
    """
    Models the Twitch drops page with various functions
        user : Account
        drops_available - Are drops still available, indefinite execution if empty : Event
        headless - Should selenium start headless if possible : Boolean
        auto_claim - Should drops be automatically claimed : Boolean
        notify_on_claim - Should username be texted on drop claim/claimable : Boolean
    """

    def __init__(self, user, drops_available=None, headless=True, auto_claim=True,
                 notify_on_claim=False, notify_no_avilable=False):
        Twitch.__init__(self, user, headless)
        self.drops = drops_available
        self.url = "https://www.twitch.tv/drops/inventory"
        self.claim = auto_claim
        self.notify_claim = notify_on_claim
        self.notify_available = notify_no_avilable

        # Setup Twilio if notifying
        if self.notify_claim or self.notify_available:
            from tell_me_done import sender
            self.notifyer = sender.Notifier()

    def run(self):
        """
        Automate checking and claiming drops in the appropriate inventory
        """
        self.setup()
        print(self.user.username, "-", datetime.now().strftime("%H:%M:%S"), "-",
              "[*] Inventory Starting.")

        self.lock.acquire()
        self.driver.get(self.url)
        self.lock.release()

        while self._check_drops_available():
            self.lock.acquire()
            self.driver.refresh()
            self.lock.release()

            self._claim_drop()

            print(self.user.username, "-",
                  datetime.now().strftime("%H:%M:%S"), "-", "[*] Drops processed.")

            time.sleep(600)

        print(self.user.username, "-", datetime.now().strftime("%H:%M:%S"),
              "-", "[*] Quitting inventory.")
        self.driver.quit()

    def _claim_drop(self):
        """
        Attempt to claim a drop in the inventory
            -> Bool
        """
        element = self._find_element_xpath(
            "//div[@data-test-selector='DropsCampaignInProgressRewards-container']//button[@data-test-selector='DropsCampaignInProgressRewardPresentation-claim-button']")
        if element != None:
            print(self.user.username, "-", datetime.now().strftime("%H:%M:%S"), "-",
                  "[*] Drop claimable.")

            # Notify drop claimable
            if self.notify_claim:
                self.notifyer.send("Drop is claimable", user=self.user)

            # Claim drop
            if self.claim:
                self._click_element_xpath(
                    "//div[@data-test-selector='DropsCampaignInProgressRewards-container']//button[@data-test-selector='DropsCampaignInProgressRewardPresentation-claim-button']")
                print(self.user.username, "-",
                      datetime.now().strftime("%H:%M:%S"), "-", "[+] Drop claimed.")

            # Wait for drop to be claimed
            else:
                while self._find_element_xpath(
                        "//div[@data-test-selector='DropsCampaignInProgressRewards-container']//button[@data-test-selector='DropsCampaignInProgressRewardPresentation-claim-button']"):
                    print(self.user.username, "-",
                          datetime.now().strftime("%H:%M:%S"), "-", "[!] Not claimed yet.")
                    time.sleep(60)

                    self.lock.acquire()
                    self.driver.refresh()
                    self.lock.release()

            return True

        return False

    def _check_drops_available(self):
        """
        Check if there are any drops left
        """
        if self.drops == None:
            return True

        if self._find_element_xpath("//div[@data-test-selector='DropsCampaignInProgressRewards-container']//img[@class='inventory-drop-image inventory-opacity-2 tw-image']") == None:
            print(self.user.username, "-", datetime.now().strftime("%H:%M:%S"), "-",
                  "[*] No more drops left.")
            self.drops.set()
            return False
        else:
            return True
