# Main program to build and run classes
from os import path
import queue
import sys
import threading
import twitch
from utility import accounts


class Person(threading.Thread):
    """Threaded class to process a queue of people.

    Pulls user account from _queue,
    sets up and proccesses their invetory and stream.

    Attributes:
        _queue : Queue - User accounts to process
        _headless : bool - Should the selenium driver be headless
        _auto_claim : bool - Should drops be automatically claimed
        _notifications : dir - Various notification settings
    """

    def __init__(
        self, people: queue.Queue, headless: bool, auto_claim: bool, notifications: dir
    ) -> None:
        threading.Thread.__init__(self)
        self._queue = people
        self._headless = headless
        self._auto_claim = auto_claim
        self._notifications = notifications

        # https://github.com/twilio/twilio-java/issues/428#issuecomment-697868934
        if self._notifications["notify user at end"]:
            import tell_me_done

            self._alerter = tell_me_done.Notifier()

    def run(self) -> None:
        """
        Process the next person by starting a stream and inventory for them
        """
        while True:
            user_account = self._queue.get()

            print(user_account.username, "-", "[*] Threading.")

            # If you can and should send them messages, send them messages
            if user_account.phone != None:
                notify_on_claim = self._notifications[
                    "notify user about claimable drops"
                ]
                notify_at_end = self._notifications["notify user at end"]
            else:
                notify_on_claim = False
                notify_at_end = False

            drops = threading.Event()
            stream = twitch.Stream(user_account, drops, headless=self._headless)
            inv = twitch.Inventory(
                user_account,
                drops,
                auto_claim=self._auto_claim,
                notify_on_claim=notify_on_claim,
                headless=self._headless,
            )

            stream.start()
            inv.start()

            # inv always ends first as it sets the drops event
            inv.join()
            stream.join()

            print(user_account.username, "-", "[*] Finished.")
            if notify_at_end:
                self._alerter.send("Your all finished", user=user_account)

            self._queue.task_done()


def run(threads: int = 0) -> None:
    """Thread and queue people.

    Pulls user accouts from storage and queues them up for Person.

    Args:
        threads : Integer > 0 - No. of threads defaults to number of users
    """

    SHUTDOWN_ON_FINISH = False  # Should the system shutdown at the end
    HEADLESS = False  # Change this to hide/show the Twitch windows
    AUTO_CLAIM = True  # Might be a bug - don't auto claim whilst playing smite
    # Should admins/users be alerted at end of program or users alerted when drops are claimable/claimed
    NOTIFICATIONS = {
        "notify admins at end": False,
        "notify user at end": False,
        "notify user about claimable drops": False,
    }

    # Setup queue
    people_queue = queue.Queue()

    print("[*] Starting")

    user_accounts = accounts.get_accounts()
    threads = len(user_accounts) if threads == 0 else threads

    # Setup threads
    for _ in range(threads):
        t = Person(people_queue, HEADLESS, AUTO_CLAIM, NOTIFICATIONS)
        # t.setDaemon(True)
        t.daemon = True
        t.start()

    # Add people to queue
    for user_account in user_accounts:
        people_queue.put(user_account)

    # After queue processed notify admins and shutdown
    people_queue.join()

    print("[*] Done")

    if NOTIFICATIONS["notify admins at end"]:
        from tell_me_done import sender

        admin_alert = sender.Notifier()
        admin_alert.notify(message="All people processed", admin_only=True)

    if SHUTDOWN_ON_FINISH:
        from utility import shutdown

        shutdown.shutdown()


if __name__ == "__main__":
    # Check for args
    if len(sys.argv) > 1 and (threads := sys.argv[1]).isdigit():
        run(threads)
    else:
        run()
