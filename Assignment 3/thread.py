import threading
from threading import Event
from functools import partial
from random import randint
import time
import datetime as dt
import logging

logging.basicConfig(
    filename="Assignment 3/output.txt", level=logging.INFO, filemode="w"
)

logger = logging.getLogger()

class Thread(threading.Thread):
    """
    This is a custom Thread class that uses
    - Stop events to completely stop a thread
    - Loops a function given a poll time
    """

    def __init__(self, name: str, **kwargs) -> None:
        """
        Creates a thread with the following parameters
            Parameters:
                name (str): name of the thread
                kwargs["time"] (int) : by default 1000 milliseconds but otherwise needs to be in milliseconds
        """
        super().__init__()
        self.created_Time = round(
            time.time() * 1000
        )  # precisely when this thread is created in milliseconds
        self.time = 1000 if "time" not in kwargs else int(kwargs.pop("time")) + 1
        self.dead_Line = self.created_Time + self.time  # soft deadline in milliseconds
        self.stop_event = Event()
        self.started = False
        self.assignment = None
        self.name = name

    def start(self):
        if not self.started and self.time != 0:
            # print(f"[{dt.datetime.now().strftime('%H:%M:%S')}]: ", f"{self.name} started")
            logger.info(
                " ".join(
                    [
                        f"[{dt.datetime.now().strftime('%H:%M:%S')}]: ",
                        f"{self.name} started |",
                        f"Service Time Left: {self.time}",
                    ]
                )
            )
            self.stop_event.clear()
            self.started = True
            return super().start()
        else:
            # print(f"[{dt.datetime.now().strftime('%H:%M:%S')}]: ", f"{self.name} running")
            logger.info(
                " ".join(
                    [
                        f"[{dt.datetime.now().strftime('%H:%M:%S')}]: ",
                        f"{self.name} running |",
                        f"Service Time Left: {self.time}",
                    ]
                )
            )
            self.stop_event.clear()

    def assign(self, partial_function, command:list):
        """ 
        Assigns the process with a function
        """
        if isinstance(partial_function, partial):
            self.assignment = partial_function
            self.assignment_comment = command

    def run(self):
        """
        Overwrites the Thread.run function with the function that needs to be ran
        """
        if self.started:
            while self.time > 0:
                if not self.stop_event.is_set():
                    # Do Tasks stuff
                    if self.time == 1:
                        # Reset the started flag when the thread finishes
                        self.started = False
                        # print(f"[{dt.datetime.now().strftime('%H:%M:%S')}]: ", f"{self.name} finished")
                        logger.info(
                            " ".join(
                                [
                                    f"[{dt.datetime.now().strftime('%H:%M:%S')}]: ",
                                    f"{self.name} finished |",
                                    f"Service Time Left: {self.time}",
                                ]
                            )
                        )
                    if self.assignment is not None:
                        logger.info(
                            " ".join(
                                [
                                    f"[{dt.datetime.now().strftime('%H:%M:%S')}]: ",
                                    f"{self.name} started {' '.join(self.assignment_comment)} |",
                                    f"Service Time Left: {self.time}",
                                ]
                            )
                        )
                        return_value = self.assignment()
                        timesleep = (randint(100, 1000))
                        time.sleep((timesleep if timesleep < self.time else self.time)/1000)
                        logger.info(
                            " ".join(
                                [
                                    f"[{dt.datetime.now().strftime('%H:%M:%S')}]: ",
                                    f"{self.name} finished {' '.join(self.assignment_comment)} value: {return_value} |",
                                    f"Service Time Left: {self.time}",
                                ]
                            )
                        )
                        self.assignment = None

                    self.time = self.dead_Line - round(time.time() * 1000)
                else:
                    # freeze count down
                    self.dead_Line = self.time + round(time.time() * 1000)
                time.sleep(0.001)

            self.started = False
            # print(f"[{dt.datetime.now().strftime('%H:%M:%S')}]: ", f"{self.name} finished")
            logger.info(
                " ".join(
                    [
                        f"[{dt.datetime.now().strftime('%H:%M:%S')}]: ",
                        f"{self.name} finished |",
                        f"Service Time Left: {self.time}",
                    ]
                )
            )

    def join(self, timeout: float = 2) -> None:
        super().join(timeout)

    def stop(self):
        if self.started and self.time > 0:
            # print(f"[{dt.datetime.now().strftime('%H:%M:%S')}]: ", self.name, "pausing")
            logger.info(
                " ".join(
                    [
                        f"[{dt.datetime.now().strftime('%H:%M:%S')}]: ",
                        self.name,
                        "stopping |",
                        f"Service Time Left: {self.time}",
                    ]
                )
            )
            self.stop_event.set()

    def status(self):
        return not self.stop_event.is_set(), (self.time > 0), (self.assignment is not None)
