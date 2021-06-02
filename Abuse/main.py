# Main program to build and run classes
import queue
import threading
import twitch
from utility import accounts


class Person(threading.Thread):
    """
    Threaded class to process a queue of people
        q - Queue of people to process : Queue
    """

    def __init__(self, q, headless, auto_claim, notifications):
        threading.Thread.__init__(self)
        self.queue = q
        self.headless = headless
        self.auto_claim = auto_claim
        self.notifications = notifications

        # https://github.com/twilio/twilio-java/issues/428#issuecomment-697868934
        if self.notifications["notify user at end"]:
            import tell_me_done
            self.alerter = tell_me_done.Notifier()

    def run(self):
        """
        Process the next person by starting a stream and inventory for them
        """
        while True:
            user_account = self.queue.get()

            print(user_account.username, "-", "[*] Threading.")

            # If you can and should send them messages, send them messages
            if user_account.phone != None:
                notify_on_claim = self.notifications["notify user about claimable drops"]
                notify_at_end = self.notifications["notify user at end"]
            else:
                notify_on_claim = False
                notify_at_end = False

            drops = threading.Event()
            stream = twitch.Stream(user_account, drops, headless=self.headless)
            inv = twitch.Inventory(
                user_account, drops, auto_claim=self.auto_claim, notify_on_claim=notify_on_claim, headless=self.headless)

            stream.start()
            inv.start()

            # inv always ends first as it sets the drops event
            inv.join()
            stream.join()

            print(user_account.username, "-", "[*] Finished.")
            if notify_at_end:
                self.alerter.send("Your all finished", user=user_account)

            self.queue.task_done()


def run(threads=0):
    """
    Thread and queue people
        threads - No. of threads defaults to number of users : Integer > 0
    """

    shutdown_on_finish = False  # Should the system shutdown at the end
    headless = False  # Change this to hide/show the Twitch windows
    auto_claim = True  # Might be a bug - don't auto claim whilst playing smite
    # Should admins/users be alerted at end of program or users alerted when drops are claimable/claimed
    notifications = {"notify admins at end": True,
                     "notify user at end": True,
                     "notify user about claimable drops": True}

    # Setup queue
    people_queue = queue.Queue()

    print("[*] Starting")

    user_accounts = accounts.get_accounts()
    threads = len(user_accounts) if threads == 0 else threads

    # Setup threads
    for _ in range(threads):
        t = Person(people_queue, headless, auto_claim, notifications)
        t.setDaemon(True)
        t.start()

    # Add people to queue
    for user_account in user_accounts:
        people_queue.put(user_account)

    # After queue processed notify admins and shutdown
    people_queue.join()

    print("[*] Done")

    if notifications["notify admins at end"]:
        from tell_me_done import sender
        admin_alert = sender.Notifier()
        admin_alert.notify(message="All people processed", admin_only=True)

    if shutdown_on_finish:
        from utility import shutdown
        shutdown.shutdown()


if __name__ == "__main__":
    import sys

    # Check for args
    if len(sys.argv) > 1:
        threads = sys.argv[1]
        run(threads)
    else:
        run()
