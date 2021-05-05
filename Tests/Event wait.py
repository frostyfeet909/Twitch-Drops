import threading
import time
timer = threading.Event()
while True:
    print("AHHHH")
    #timer.wait(10)
    time.sleep(10)
    print("Finished")
    break
