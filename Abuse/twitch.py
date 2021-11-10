# Objects to model Twitch screens
from datetime import datetime
from os import path
import platform
import threading
import time
from selenium import webdriver
from selenium.webdriver.common import keys
from selenium.webdriver.chrome import options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import (
    ElementNotInteractableException,
    TimeoutException,
    WebDriverException,
)
import account
from utility import time_lock


class Twitch(threading.Thread):
    """Models a Twitch page with various functions.

    Provides various ways to login to Twitch as well as interact with elemets via xpath.

    Attributes:
        user : Account - A user account object
        _driver : WebDriver - The selenium chrome webdriver
        _headless : bool - Should selenium start headless if possible
        _lock : Time_Lock - A lock to stop rapid interaction with Twitch
        _url : str - The url
    """

    def __init__(self, user: account.Account, headless: bool = False) -> None:
        threading.Thread.__init__(self)
        self.user = user
        self._driver = None
        self._headless = headless
        self._lock = (
            time_lock.Time_Lock()
        )  # Make sure interaction has at least 2 second timeout
        self._url = None

    def run(self) -> bool:
        # TODO : Maybe rename validate_account
        """Verify login data for the Twitch account.

        Returns:
            Whether the provided user account is a valid Twith account.
        """
        self._setup_webdriver()
        valid = self._verify_account()
        self._driver.quit()
        return valid

    def _setup(self) -> None:
        """Setup Twitch page.

        This involves loging in and seting up the selenium webdriver.
        """
        print(self.user.username, "-", self._date_time(), "-", "[*] Twitch Starting.")

        # If headless required, must ensure cookies exsist
        if self.user.cookies == None and self._headless:
            need_login = True
        else:
            need_login = False

        self._setup_webdriver(need_login)

        # Check successful login
        if not self._login():
            print(self.user.username, "-", "[!!] Could not login.")
            raise PermissionError

        if need_login:
            self._setup_webdriver()

    def _setup_webdriver(self, cannot_headless: bool = False) -> None:
        """Setup the selenium webdriver.

        Returning is pointless as an exceptio occurs if the driver is not setup.

        Args:
            cannot_headless : bool - Cannot be headless if manual login is required

        Raises:
            EnvironmentError - The platform is not supported
            FileNotFoundError - The webdriver cannot be found
        """

        if self._driver != None:
            self._driver.quit()

        # Find webdriver as the webdriver is stored differently on OS's
        plat = platform.platform().lower()

        if plat.startswith("win"):
            file_loc = path.join(
                path.dirname(path.realpath(__file__)),
                "resources",
                "webdrivers",
                "chromedriver.exe",
            )
        elif plat.startswith("lin"):
            file_loc = "/usr/lib/chromium-browser/chromedriver"
        else:
            print(self.user.username, "-", "[!!] Platform not supported.")
            raise EnvironmentError

        if not path.isfile(file_loc):
            print(self.user.username, "-", "[!!] Chromium webdriver does not exsist!")
            raise FileNotFoundError

        # Setup webdriver
        chrome_options = options.Options()
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--mute-audio")

        # Need not headless for login
        if not cannot_headless and self._headless:
            chrome_options.add_argument("--headless")
        elif self._headless:
            print(self.user.username, "-", "[!] No cookie file - must login manually.")

        self._driver = webdriver.Chrome(
            executable_path=file_loc, chrome_options=chrome_options
        )

    def _login(self) -> bool:  # TODO : Handle no cookies and no password better
        """Login to Twitch.

        Prioritise logging in quickly with cookies,
        have to use locks as another thread maybe attempting to the same thing.
        Checks if another thread has azquired cookies otherwise will force manual login.

        Returns:
            Is the user logged in.
        """
        logged_in = False

        if self.user.cookies == None:
            # Check if cookies have just been added
            self.user.lock.acquire()
            self.user.load()

            if self.user.cookies != None:
                # Cookies! :D
                self.user.lock.release()
                logged_in = self._login_by_cookies()
            else:
                # No cookies :(
                logged_in = self._login_by_Twitch()
                self.user.lock.release()
                return logged_in
        else:
            # Cookies! :D
            logged_in = self._login_by_cookies()

        # As a last effort try manual login
        if not logged_in:
            logged_in = self._login_by_Twitch()

        return logged_in

    def _verify_account(self, check_robot: bool = True) -> bool:
        """Verify the user account can login.

        if a robot check is true then verification cannot be completed
        but this does not matter if the account details do not need to be verified,
        this is because the account is first verified when a manual login is required.

        Args:
            check_robot : bool - Should a robot check be done.

        Returns:
            The user could/couldn't be verified.

        Raises:
            WebDriverException - Possible the webdriver lost connection.
            LookupError - Verification was not possible due to anti-robot checks on Twitch. (try changing IP)
        """
        if not self.user.password:
            return False

        # Check for internet
        try:
            self._lock.acquire()
            self._driver.get("https://www.Twitch.tv/login")
            self._lock.release()
        except WebDriverException:
            raise WebDriverException("[!!] Do you have internet?")

        # Enter username
        username_element = self._find_element_xpath("//input[@id='login-username']")
        self._lock.acquire()
        username_element.send_keys(self.user.username)
        self._lock.release()

        # Enter password
        password_element = self._find_element_xpath("//input[@id='password-input']")
        self._lock.acquire()
        password_element.send_keys(self.user.password)
        password_element.send_keys(keys.Keys.RETURN)
        self._lock.release()

        if check_robot and self._check_not_robot():
            print(
                "[!!] Robot checks are in force - could not verify \n  try changing your ip"
            )
            raise LookupError

        alert_window = self._find_element_xpath(
            "//div[contains(@class, 'server-message-alert')]//strong"
        )

        return alert_window == None

    def _login_by_Twitch(self) -> bool:
        """Login to Twitch through the Twitch login page.

        Returns:
            The success of the login.
        """
        if not self._verify_account(False):
            print("[!!] Unable to login with username, password")
            return False

        # Checks for various traps - sometimes in different orders so verifies no checks still remain
        # Slow but effective
        checks = True
        while checks:
            checks = False
            while self._check_auth():
                checks = True
                print(self.user.username, "-", "[!] Auth verification required.")
                time.sleep(10)

            while self._check_not_robot():
                checks = True
                print(self.user.username, "-", "[!] Robot verification required.")
                time.sleep(10)

            while self._check_need_verify():
                checks = True
                print(self.user.username, "-", "[!] New login verification required.")
                time.sleep(10)

        self.user.login(self._driver.get_cookies())
        return True

    def _login_by_cookies(self) -> bool:  # TODO : Check cookies are good
        """Login to Twitch by using cookies stored in the account.

        Returns:
            The success of the login.
        """
        self._lock.acquire()
        self._driver.get("https://www.Twitch.tv")
        self._lock.release()

        cookies = self.user.cookies

        try:
            for cookie in cookies:
                self._driver.add_cookie(cookie)
        except:
            # TODO : Maybe clear user cookies
            print("[!!] Cookie error.")
            return False

        self._lock.acquire()
        self._driver.refresh()
        self._lock.release()
        return True

    def _check_need_verify(self) -> bool:
        """Check need to verify new login."""
        if self._find_element_xpath("//h4[contains(text(), 'Verify')]") != None:
            return True

        return False

    def _check_auth(self) -> bool:
        """Check need to enter user authentication."""
        if self._find_element_xpath("//label[contains(text(), 'Token')]") != None:
            return True

        return False

    def _check_not_robot(self) -> bool:
        """Check need to verify not a robot :3"""
        # Wait 10 seconds incase page isn't fully loaded
        try:
            WebDriverWait(self._driver, 10).until(
                lambda d: d.find_element_by_id("FunCaptcha")
            )  # not tested
        except TimeoutException:
            return False

        return True

    def _find_element_xpath(self, xpath: str) -> WebElement:
        """Find and return element by xpath.

        Args:
            xpath : str - xpath of element

        Returns:
            The interactable web element.
        """
        # Wait 10 seconds incase page isn't fully loaded
        try:
            element = WebDriverWait(self._driver, 10).until(
                lambda d: d.find_element_by_xpath(xpath)
            )
        except TimeoutException:
            element = None
        except WebDriverException:
            element = None
            print(
                self.user.username,
                "-",
                self._date_time(),
                "-",
                "[!] Somethign funny happened with the webdriver.",
            )

            self._setup()

        return element

    def _click_element_xpath(self, xpath: str) -> bool:
        """Find and click element by xpath.

        Args:
            xpath : str - xpath of element

        Returns:
            Was the click successful.
        """
        element = self._find_element_xpath(xpath)

        if element != None:
            self._lock.acquire()

            try:
                element.click()
            except ElementNotInteractableException:
                self._lock.release()
                return False

            self._lock.release()
            return True

        return False

    @staticmethod
    def _date_time(file_friendly: bool = False) -> str:
        """Static method to get the datetime in a readable format."""
        if not file_friendly:
            return datetime.now().strftime("%H:%M:%S")
        else:
            return datetime.now().strftime("%H-%M-%S")


class Stream(Twitch):
    """Models a Twitch stream page with various functions.

    Provides various ways to of interacting with the stream to increase performance and find streams.
    See base class for additional details.

    Attributes:
        _chat : bool Should chat be left on
        _drops : Event - Are drops still available, indefinite execution if empty
        _url : str - URL for directory of droppable streams
    """

    def __init__(
        self,
        user: account.Account,
        drops_available: threading.Event = None,
        headless: bool = True,
        chat_on: bool = False,
    ) -> None:
        Twitch.__init__(self, user, headless)
        self._chat = chat_on
        self._drops = drops_available
        self._url = "https://www.Twitch.tv/directory/game/SMITE/tags/c2542d6d-cd10-4532-919b-3d19f30a768b"

    def run(self) -> None:
        """Automate finding and watching droppable streams.

        Twitch setup,
        then while drops are available dearch the _url for droppabale streams and Optimise streams.
        """
        self._setup()

        while not self._drops.is_set() if self._drops != None else True:
            # If no stream find and optimise stream
            if not self._check_stream_alive():
                if self._find_stream():
                    self._optimise_stream()
            else:
                print(
                    self.user.username,
                    "-",
                    self._date_time(),
                    "-",
                    "[*] Stream Running.",
                )
                if self._chat:
                    self._claim_channel_points()

            time.sleep(600)

            if self._check_error():
                print(
                    self.user.username,
                    "-",
                    self._date_time(),
                    "-",
                    "[!] Network error.",
                )
                self._setup()

        print(self.user.username, "-", self._date_time(), "-", "[*] Quitting stream.")
        self._driver.quit()

    def _setup(self) -> None:
        """See base class."""
        Twitch._setup(self)
        print(self.user.username, "-", self._date_time(), "-", "[*] Stream Starting.")

    def _optimise_stream(self) -> None:
        """Optimise current stream to lower resources.

        Does this by configuring stream quality and chat settings.
        """
        self._click_element_xpath(
            "//button[@data-a-target='player-overlay-mature-accept']"
        )  # Accept mature stream
        self._lower_quality()

        if not self._chat:
            # Turn chat off
            self._click_element_xpath(
                "//div[@data-a-target='right-column-chat-bar']//button[@data-a-target='right-column__toggle-collapse-btn']"
            )

    def _find_stream(self) -> bool:
        """Find and goto a new stream.

        Returns:
            Whether a new stream has been entered.
        """
        self._lock.acquire()
        self._driver.get(self._url)
        self._lock.release()

        # Click on first valid stream
        if not self._click_element_xpath(
            "//div[@data-target='directory-first-item']//a[@data-a-target='preview-card-title-link']"
        ):
            print(
                self.user.username,
                "-",
                self._date_time(),
                "-",
                "[!] New stream not found.",
            )
            return False

        print(self.user.username, "-", self._date_time(), "-", "[*] New stream found.")
        print("    - %s" % self._driver.current_url)
        return True

    def _check_stream_alive(self) -> bool:
        """Check if current stream is still live and dropping."""
        # Check stream live and dropping, some streams (smitegame) go 'offline' meaning no drops but still live
        if not (
            self._find_element_xpath(
                "//div[@class='channel-info-content']//p[contains(text(), 'LIVE')]"
            )
            or self._find_element_xpath(
                "//div[@class='channel-info-content']//a[@data-a-target='Drops Enabled']"
            )
        ):
            print(
                self.user.username, "-", self._date_time(), "-", "[!] Stream offline."
            )
            return False

        return True

    def _claim_channel_points(self) -> None:
        """Claim channel points."""
        self._click_element_xpath("//div[@class='claimable-bonus__icon tw-flex']")

    def _lower_quality(self, quality: str = None) -> None:
        """Lower quality of stream.

        Tries to set to desired quality otherwise will go with the lowest option available.
        """
        # Menu button
        self._click_element_xpath("//button[@data-a-target='player-settings-button']")

        # Dropdown button
        self._click_element_xpath(
            "//button[@data-a-target='player-settings-menu-item-quality']"
        )

        # Trying lowest quality buttons
        if quality == None:
            for quality_setting in ["160p", "360p", "480p", "720p", "Auto"]:
                if self._click_element_xpath(
                    "//div[@data-a-target='player-settings-submenu-quality-option']//div[contains(text(), '%s')]"
                    % quality_setting
                ):
                    break
        else:
            self._click_element_xpath(
                "//div[@data-a-target='player-settings-submenu-quality-option']//div[contains(text(), '%s')]"
                % quality
            )

    def _check_error(self) -> bool:
        """Check for an error inside te player."""
        return None != self._find_element_xpath("//p[contains(text(), 'Error')]")


class Inventory(Twitch):
    """Models a Twitch inventory page with various functions.

    Provides various ways to of interacting with the inventory to claim and monitor drops.
    See base class for additional details.

    Attributes:
        _claim : bool - Should drops be automatically claimed
        _notify_on_claim : bool - Should username be texted on drop claim/claimable
        _drops : Event - Are drops still available, will be set when inventory is empty, indefinite execution if empty
    """

    def __init__(
        self,
        user: account.Account,
        drops_available: threading.Event = None,
        headless: bool = True,
        auto_claim: bool = True,
        notify_on_claim: bool = False,
        notify_no_avilable: bool = False,
    ) -> None:
        Twitch.__init__(self, user, headless)
        self._drops = drops_available
        self._url = "https://www.Twitch.tv/drops/inventory"
        self._claim = auto_claim
        self._notify_claim = notify_on_claim  # TODO : not used
        self._notify_available = notify_no_avilable

        # Setup Twilio if notifying
        if self._notify_claim or self._notify_available:
            from tell_me_done import sender

            self.notifyer = sender.Notifier()

    def run(self) -> None:
        """Automate checking and claiming drops."""
        self._setup()

        while self._check_drops_available():
            self._claim_drop()

            print(
                self.user.username, "-", self._date_time(), "-", "[*] Drops processed."
            )

            time.sleep(600)

            self._lock.acquire()
            self._driver.refresh()
            self._lock.release()

            if self._check_error():
                print(
                    self.user.username,
                    "-",
                    self._date_time(),
                    "-",
                    "[!] Network error.",
                )
                self._setup()

        print(
            self.user.username, "-", self._date_time(), "-", "[*] Quitting inventory."
        )

        self._driver.quit()

    def _setup(self) -> None:
        """See base class."""
        Twitch._setup(self)

        print(
            self.user.username, "-", self._date_time(), "-", "[*] Inventory Starting."
        )

        self._lock.acquire()
        self._driver.get(self._url)
        self._lock.release()

    def _claim_drop(self) -> bool:
        """Attempt to claim a drop in the inventory.

        Check again for droppable,
        will notify the user if needed then claim dependant on _auto_claim.
        Will pause if the user needs to collect maually."""
        element = self._find_element_xpath(
            "//div[@data-test-selector='DropsCampaignInProgressRewards-container']//button[@data-test-selector='DropsCampaignInProgressRewardPresentation-claim-button']"
        )
        if element != None:
            print(
                self.user.username, "-", self._date_time(), "-", "[*] Drop claimable."
            )

            # Notify drop claimable
            if self._notify_claim:
                self.notifyer.send("Drop is claimable", user=self.user)

            # Claim drop
            if self._claim:
                self._click_element_xpath(
                    "//div[@data-test-selector='DropsCampaignInProgressRewards-container']//button[@data-test-selector='DropsCampaignInProgressRewardPresentation-claim-button']"
                )
                print(
                    self.user.username, "-", self._date_time(), "-", "[+] Drop claimed."
                )

            # Wait for drop to be claimed
            else:
                while self._find_element_xpath(
                    "//div[@data-test-selector='DropsCampaignInProgressRewards-container']//button[@data-test-selector='DropsCampaignInProgressRewardPresentation-claim-button']"
                ):
                    print(
                        self.user.username,
                        "-",
                        self._date_time(),
                        "-",
                        "[!] Not claimed yet.",
                    )
                    time.sleep(60)

                    self._lock.acquire()
                    self._driver.refresh()
                    self._lock.release()

            return True

        return False

    def _check_drops_available(self) -> bool:
        """Check if there are any drops left."""
        if self._drops == None:
            return True

        if (
            self._find_element_xpath(
                "//div[@data-test-selector='DropsCampaignInProgressRewards-container']//img[@class='inventory-drop-image inventory-opacity-2 tw-image']"
            )
            == None
        ):
            print(
                self.user.username,
                "-",
                self._date_time(),
                "-",
                "[*] No more drops left.",
            )

            self._drops.set()
            return False
        else:
            return True

    def _check_error(self) -> bool:
        """Check for an network error where screen is not loaded."""
        return not (
            self._find_element_xpath("//h4[contains(text(), 'Claimed')]")
            or self._find_element_xpath("//p[contains(text(), 'In Progress')]")
        )
