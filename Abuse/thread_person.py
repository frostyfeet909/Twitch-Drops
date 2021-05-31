# Threaded class to process people
import threading
import queue
import twitch
import account
import tell_me_done


class Thread_person(threading.Thread):
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

    def run(self):
        """
        Process the next person by starting a stream and inventory for them
        """
        while True:
            user_account = self.queue.get()

            print(user_account.username, "-", "[*] Threading.")

            # If you can and should send them messages, send them messages
            if user_account.phone != None and self.notifications:
                person_alert = tell_me_done.Notifier()
                notify = True
            else:
                notify = False

            drops = threading.Event()
            stream = twitch.Stream(user_account, drops, headless=self.headless)
            inv = twitch.Inventory(
                user_account, drops, auto_claim=self.auto_claim, notify_on_claim=notify, headless=self.headless)

            stream.start()
            inv.start()

            # inv always ends first as it sets the drops event
            inv.join()
            stream.join()

            print(user_account.username, "-", "[*] Finished.")
            if notify:
                person_alert.send("Your all finished", user=user_account)

            self.queue.task_done()
