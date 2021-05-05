# Program to instanciate Time Lock class
from time import time, sleep
from random import randint


class Time_Lock:
    """
    Class to imitate threading.Lock based on a timeout
        timeout - Required locking timout : Float >= 0
        variance - % Maximum variance in the timeout : Integer >= 0
    """

    def __init__(self, timeout=2, variance=0):
        self.last_time = 0
        self.timeout = timeout
        self.variance = variance

        if timeout < 0 or variance < 0:
            print("[!!] timeout and variance must be above 0")
            raise ValueError

    def acquire(self):
        """
        Acquire timeout lock
        """
        time_diff = time()-self.last_time
        timeout = self.timeout + self.timeout*randint(0, self.variance)/100

        # Sleep untill timeout is over
        if time_diff < timeout:
            sleep((timeout-time_diff))

    def release(self):
        """
        Release timeout lock
        """
        self.last_time = time()
