# Main program to build and run classes


def run(threads=2):
    """
    Thread and queue people
        threads - No. of threads : Integer > 0
    """
    import queue
    import thread_person
    from utility import accounts

    shutdown_on_finish = False  # Should the system shutdown at the end
    alert_at_end = True  # Should the admins be messages at the end - notifications must be True
    headless = False  # Change this to hide/show the Twitch windows
    auto_claim = True  # Might be a bug - don't auto claim whilst playing smite
    notifications = True  # Turn off if you do not have Twilio

    # Setup queue
    people_queue = queue.Queue()

    print("[*] Starting")

    # Setup threads
    for _ in range(threads):
        t = thread_person.Thread_person(
            people_queue, headless, auto_claim, notifications)
        t.setDaemon(True)
        t.start()

    # Add people to queue
    user_accounts = accounts.get_accounts()

    for user_account in user_accounts:
        people_queue.put(user_account)

    # After queue processed notify admins and shutdown
    people_queue.join()

    print("[*] Done")

    if alert_at_end and notifications:
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
