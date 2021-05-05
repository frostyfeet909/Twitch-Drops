# Main program to build and run classes


def run(threads=2, shutdown_on_finish=False, alert_at_end=True):
    """
    Thread and queue people
        threads - No. of threads : Integer > 0
    """
    import queue
    import thread_person
    import account
    import os
    from os import path
    from utility import accounts

    # Setup queue
    people_queue = queue.Queue()

    print("[*] Starting")

    # Setup threads
    for _ in range(threads):
        t = thread_person.Thread_person(people_queue)
        t.setDaemon(True)
        t.start()

    # Add people to queue
    user_accounts = accounts.get_accounts()

    for user_account in user_accounts:
        people_queue.put(user_account)

    # After queue processed notify admins and shutdown
    people_queue.join()

    if alert_at_end:
        from tell_me_done import sender
        admin_alert = sender.Notifier()
        admin_alert.notify(message="All people processed", admin_only=True)

    if shutdown_on_finish:
        from utility import shutdown
        shutdown.shutdown()


if __name__ == "__main__":
    import sys

    # Check for args
    if len(sys.argv) > 3:
        threads = sys.argv[1]
        shutdown = sys.argv[2]
        alert = sys.argv[3]
        run(threads, shutdown, alert)
    else:
        run()
