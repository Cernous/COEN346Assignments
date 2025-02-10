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
  def __init__(self, name: str, command, **kwargs) -> None:
    '''
        Creates a thread with the following parameters
            Parameters:
                name (str): name of the thread
                command (function): partial or full function 
                kwargs["time"] (float) : by default 2 seconds unless specified (poll rate or function run rate)
    '''
    super().__init__()
    self.name = name
    self.partial_command = command

  def run(self):
    '''
        Overwrites the Thread.run function with the function that needs to be ran
    '''
    print(f"[{dt.datetime.now().strftime('%H:%M:%S')}]: ", f"{self.name} running")
    logger.info(" ".join([f"[{dt.datetime.now().strftime('%H:%M:%S')}]: ", f"{self.name} running"]))
    out = None
    try:
      out = self.partial_command()
    except Exception as e:
      # made to prevent deadlocks ("release an unlocked lock (mutex)")
      print(f"[{dt.datetime.now().strftime('%H:%M:%S')}]: ", self.name, str(e))
      logger.info(" ".join([f"[{dt.datetime.now().strftime('%H:%M:%S')}]: ", self.name, str(e)]))
    print(f"[{dt.datetime.now().strftime('%H:%M:%S')}]: ", f"{self.name} done running", out)
    logger.info(" ".join([f"[{dt.datetime.now().strftime('%H:%M:%S')}]: ", f"{self.name} done running", str(out)]))
    return out

  def join(self, timeout: float = 2) -> None:
    print(f"[{dt.datetime.now().strftime('%H:%M:%S')}]: ", f"{self.name} joining main thread")
    super().join(timeout)