# Threaded class to process people
import threading
import queue
import twitch
import account
from tell_me_done import sender


class Thread_person(threading.Thread):
    """
    Threaded class to process a queue of people
        q - Queue of people to process : Queue
    """

    def __init__(self, q):
        threading.Thread.__init__(self)
        self.queue = q

    def run(self):
        """
        Process the next person by starting a stream and inventory for them
        """
        while True:
            headless = False  # Change this to hide/show the Twitch windows
            auto_claim = True  # Might be a bug - don't auto claim whilst playing smite

            user_account = self.queue.get()

            print(user_account.username, "-", "[*] Threading.")

            if user_account.phone != None:
                person_alert = sender.Notifier()
                notify = True
            else:
                notify = False

            drops = threading.Event()
            stream = twitch.Stream(user_account, drops, headless=headless)
            inv = twitch.Inventory(
                user_account, drops, auto_claim=auto_claim, notify_on_claim=notify, headless=headless)

            stream.start()
            inv.start()

            # inv always ends first as it sets the drops event
            inv.join()
            stream.join()

            print(user_account.username, "-", "[*] Finished.")
            if notify:
                person_alert.send("Your all finished", user=user_account)

            self.queue.task_done()
