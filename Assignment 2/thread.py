import threading
from threading import Event
import time
import datetime as dt
import logging

logging.basicConfig(
  filename="Assignment 1/output.txt",
  level=logging.INFO,
  filemode='w'
)

logger = logging.getLogger()

class Thread(threading.Thread):
  """
  This is a custom Thread class that uses
  - Stop events to completely stop a thread
  - Loops a function given a poll time
  """
  def __init__(self, name: str, **kwargs) -> None:
    '''
        Creates a thread with the following parameters
            Parameters:
                name (str): name of the thread
                kwargs["time"] (int) : by default 2 seconds unless specified (poll rate or function run rate)
    '''
    super().__init__()
    self.time = 1000 if "time" not in kwargs else int(kwargs.pop("time"))
    self.stop_event = Event()
    self.started = False
    self.name = name

  def start(self):
    if not self.started:
      print(f"[{dt.datetime.now().strftime('%H:%M:%S')}]: ", f"{self.name} started")
      logger.info(" ".join([f"[{dt.datetime.now().strftime('%H:%M:%S')}]: ", f"{self.name} started"]))
      self.stop_event.clear()
      self.started = True
      return super().start()
    else:
      print(f"[{dt.datetime.now().strftime('%H:%M:%S')}]: ", f"{self.name} running")
      logger.info(" ".join([f"[{dt.datetime.now().strftime('%H:%M:%S')}]: ", f"{self.name} running"]))
      self.stop_event.clear()

  def run(self):
    '''
        Overwrites the Thread.run function with the function that needs to be ran
    '''
    if self.started:
      while self.time > 0:
        if not self.stop_event.is_set():
          # Do Tasks stuff
          self.time -= 1
          # out = partial
        time.sleep(1)
      print(f"[{dt.datetime.now().strftime('%H:%M:%S')}]: ", f"{self.name} finished")
      logger.info(" ".join([f"[{dt.datetime.now().strftime('%H:%M:%S')}]: ", f"{self.name} finished"]))
      self.started = False
      # return out

  def join(self, timeout: float = 2) -> None:
    super().join(timeout)

  def stop(self):
    if self.started:
      print(f"[{dt.datetime.now().strftime('%H:%M:%S')}]: ", self.name, "pausing")
      logger.info(" ".join([f"[{dt.datetime.now().strftime('%H:%M:%S')}]: ", self.name, "pausing"]))
      self.stop_event.set()

  def status(self):
    return not self.stop_event.is_set(), (self.time>0)