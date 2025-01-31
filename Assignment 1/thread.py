import threading
from threading import Event
import time
import datetime as dt

class Thread(threading.Thread):

  def __init__(self, name: str, command, **kwargs) -> None:
    '''
        Creates a thread with the following parameters
            Parameters:
                name (str): name of the thread
                command (function): partial or full function 
                stop_event (Event): Event to stop the thread from running
                kwargs["time"] (float) : by default 2 seconds unless specified (poll rate or function run rate)
    '''
    super().__init__()
    # Poll time by default is 2 unless specified
    self.poll_time = None if "time" not in kwargs else kwargs.pop("time")
    self.stop_event = Event()
    self.name = name
    self.partial_command = command

  def run(self):
    '''
        Overwrites the Thread.run function with the function that needs to be ran
    '''
    print(f"[{dt.datetime.now().strftime('%H:%M:%S')}]: ", f"{self.name} running")
    self.stop_event.clear()
    out = None
    while True:
      if self.poll_time is not None and (type(self.poll_time) is float or type(self.poll_time) is int):   
        try:
          out = self.partial_command()
        except Exception as e:
          # made to prevent deadlocks ("release an unlocked lock (mutex)")
          print(f"[{dt.datetime.now().strftime('%H:%M:%S')}]: ", self.name, str(e))
        # SLEEP NO RUN
        time.sleep(self.poll_time)
      else:
        # if no looping is required then just execute the command once 
        out = self.partial_command()
        self.stop_event.set()

      if self.stop_event.is_set():
        # if a stop event is set then finish the execution of the partial command and break from the loop 
        # so that the thread can join without stalling
        break
    print(f"[{dt.datetime.now().strftime('%H:%M:%S')}]: ", f"{self.name} done running", out)
    return out

  def stop(self):
    self.stop_event.set()
  
  def is_Done(self):
    return self.stop_event.is_set()

  def join(self, timeout: float = 2) -> None:
    print(f"[{dt.datetime.now().strftime('%H:%M:%S')}]: ", f"{self.name} joining main thread")
    super().join(timeout)