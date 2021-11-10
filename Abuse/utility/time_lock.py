# Program to instanciate Time Lock class
import time
import random


class Time_Lock:
    """Class to imitate threading.Lock based on a timeout.

    Attributes:
        timeout - Required locking timout : Float >= 0
        variance - % Maximum variance in the timeout : Integer >= 0
    """

    def __init__(self, timeout: int = 2, variance: int = 0) -> None:
        self.last_time = 0
        self.timeout = timeout
        self.variance = variance

        if timeout < 0 or variance < 0:
            raise ValueError("[!!] timeout and variance must be above 0")

    def acquire(self) -> None:
        """Acquire timeout lock."""
        time_diff = time.time() - self.last_time
        timeout = self.timeout + self.timeout * random.randint(0, self.variance) / 100

        # Sleep untill timeout is over
        if time_diff < timeout:
            time.sleep((timeout - time_diff))

    def release(self) -> None:
        """Release timeout lock."""
        self.last_time = time.time()
