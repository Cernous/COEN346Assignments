import threading
from threading import Event
import time
import datetime as dt
import logging
import queue
import os
import random

logging.basicConfig(
  filename="Assignment 3/output.txt",
  level=logging.INFO,
  filemode='w'
)

logger = logging.getLogger()

"""
Instructions for Threads:
- run() always loops and checks if there is a command assigned to it
  - If a command has been assigned, complete the command and do time.sleep(randint(100, 1000)/1000) to simulate an API call
  - If self.time is 0, then you stop running like in assignment 2
  - If self.time > 1000, the thread must be made available to get assigned a command (i.e set the status to something other than Finished/Paused) otherwise you shouldnt accept any
- Create any function that you want to be assigned a command keep in mind that this file will need imports from the memory/disk functions that Justin is doing
"""

class Thread(threading.Thread):
  """
  This is a custom Thread class that uses
  - Stop events to completely stop a thread
  - Loops a function given a poll time
  - Memory management capabilities (if configured as a memory manager)
  """
  def __init__(self, name: str, **kwargs) -> None:
    '''
        Creates a thread with the following parameters
            Parameters:
                name (str): name of the thread
                kwargs["time"] (int) : by default 2 seconds unless specified (poll rate or function run rate)
                kwargs["is_memory_manager"] (bool): if True, the thread functions as a memory manager
                kwargs["memory_size"] (int): number of memory pages available (only for memory manager)
                kwargs["command_queue"] (Queue): queue for memory commands (only for memory manager)
                kwargs["clock"] (object): shared clock object (only for memory manager)
                kwargs["disk_file"] (str): path to virtual disk file (only for memory manager)
    '''
    super().__init__()
    self.time = 1000 if "time" not in kwargs else int(kwargs.pop("time"))+1
    self.stop_event = Event()
    self.started = False
    self.name = name
    
    # Memory manager configuration
    self.is_memory_manager = kwargs.get("is_memory_manager", False)
    if self.is_memory_manager:
      self.memory_size = kwargs.get("memory_size", 2)  # Default to 2 pages
      self.memory = {}  # Dictionary to store pages in memory (variableId -> page)
      self.command_queue = kwargs.get("command_queue")
      self.clock = kwargs.get("clock")
      self.disk_file = kwargs.get("disk_file", "Assignment 3/vm.txt")
      self.memory_lock = threading.Lock()  # For thread-safe memory operations
      
      # Initialize disk file if it doesn't exist
      if not os.path.exists(self.disk_file):
          with open(self.disk_file, 'w') as f:
              pass  # Create empty file

  def start(self):
    if not self.started and self.time != 0:
      #print(f"[{dt.datetime.now().strftime('%H:%M:%S')}]: ", f"{self.name} started")
      logger.info(" ".join([f"[{dt.datetime.now().strftime('%H:%M:%S')}]: ", f"{self.name} started"]))
      self.stop_event.clear()
      self.started = True
      return super().start()
    else:
      #print(f"[{dt.datetime.now().strftime('%H:%M:%S')}]: ", f"{self.name} running")
      logger.info(" ".join([f"[{dt.datetime.now().strftime('%H:%M:%S')}]: ", f"{self.name} running"]))
      self.stop_event.clear()

  def run(self):
    '''
        Overwrites the Thread.run function with the function that needs to be ran
    '''
    if self.started:
        if self.is_memory_manager:
            # Memory manager execution loop
            while not self.stop_event.is_set():
                try:
                    # Get command with timeout to allow for checking if thread should stop
                    command = self.command_queue.get(timeout=0.1)
                    if command:
                        command_type, variable_id, *args = command
                        
                        # Process command based on type
                        if command_type == "Store":
                            value, response_queue = args
                            self.store(variable_id, value, response_queue)
                        elif command_type == "Release":
                            response_queue = args[0]
                            self.release(variable_id, response_queue)
                        elif command_type == "Lookup":
                            response_queue = args[0]
                            self.lookup(variable_id, response_queue)
                        
                        # Mark command as done
                        self.command_queue.task_done()
                        
                        # Simulate API call delay
                        time.sleep(random.randint(100, 300)/1000)
                except queue.Empty:
                    # No commands in queue, continue checking
                    pass
                except Exception as e:
                    logger.error(f"Memory Manager error: {e}")
        else:
            # Regular thread execution loop
            while self.time > 0:
                if not self.stop_event.is_set():
                    # Do Tasks stuff
                    if self.time == 1:
                        # Reset the started flag when the thread finishes
                        self.started = False
                        #print(f"[{dt.datetime.now().strftime('%H:%M:%S')}]: ", f"{self.name} finished")
                        logger.info(" ".join([f"[{dt.datetime.now().strftime('%H:%M:%S')}]: ", f"{self.name} finished"]))
                    self.time -= 1
                time.sleep(0.001)   

  def join(self, timeout: float = 2) -> None:
    super().join(timeout)

  def stop(self):
    if self.started and self.time > 0:
      #print(f"[{dt.datetime.now().strftime('%H:%M:%S')}]: ", self.name, "pausing")
      logger.info(" ".join([f"[{dt.datetime.now().strftime('%H:%M:%S')}]: ", self.name, "pausing"]))
      self.stop_event.set()

  def status(self):
    return not self.stop_event.is_set(), (self.time>0)
  
  # Memory management functions
  def store(self, variable_id, value, response_queue=None):
    """
    Store a variable in memory, potentially evicting another variable
    
    Parameters:
        variable_id (str): ID of the variable to store
        value (int): Value to store
        response_queue (Queue): Queue to send response back to caller
    """
    if not self.is_memory_manager:
        return
        
    with self.memory_lock:
        # Log the Store operation
        logger.info(f"Clock: {self.clock.get_time()}, Process {self.name.split()[-1] if ' ' in self.name else 'Unknown'}, Store: Variable {variable_id}, Value: {value}")
        
        # Create page with current access time
        page = {
            "variableId": variable_id,
            "value": value,
            "lastAccessTime": self.clock.get_time()
        }
        
        # Check if memory is full and we need to evict
        if variable_id not in self.memory and len(self.memory) >= self.memory_size:
            evicted_id = self._evict_lru()
            if evicted_id:
                logger.info(f"Clock: {self.clock.get_time()}, Memory Manager, SWAP: Variable {variable_id} with Variable {evicted_id}")
        
        # Store in memory
        self.memory[variable_id] = page
        
        # Return success if response queue provided
        if response_queue:
            response_queue.put(True)
  
  def release(self, variable_id, response_queue=None):
    """
    Release a variable from memory
    
    Parameters:
        variable_id (str): ID of the variable to release
        response_queue (Queue): Queue to send response back to caller
    """
    if not self.is_memory_manager:
        return
        
    with self.memory_lock:
        if variable_id in self.memory:
            # Log the Release operation
            logger.info(f"Clock: {self.clock.get_time()}, Process {self.name.split()[-1] if ' ' in self.name else 'Unknown'}, Release: Variable {variable_id}")
            
            # Remove from memory
            del self.memory[variable_id]
            
            # Remove from disk if present
            self._remove_from_disk(variable_id)
            
            # Return success
            if response_queue:
                response_queue.put(True)
        else:
            # Variable not found
            if response_queue:
                response_queue.put(False)
  
  def lookup(self, variable_id, response_queue):
    """
    Look up a variable in memory or disk
    
    Parameters:
        variable_id (str): ID of the variable to look up
        response_queue (Queue): Queue to send response back to caller
    """
    if not self.is_memory_manager:
        return
        
    with self.memory_lock:
        # Check if in memory
        if variable_id in self.memory:
            # Update access time
            self.memory[variable_id]["lastAccessTime"] = self.clock.get_time()
            # Log the Lookup operation
            logger.info(f"Clock: {self.clock.get_time()}, Process {self.name.split()[-1] if ' ' in self.name else 'Unknown'}, Lookup: Variable {variable_id}, Value: {self.memory[variable_id]['value']}")
            # Return value
            if response_queue:
                response_queue.put(self.memory[variable_id]["value"])
            return
        
        # Not in memory, check disk
        disk_value = self._read_from_disk(variable_id)
        if disk_value is not None:
            # Need to swap in from disk
            if len(self.memory) >= self.memory_size:
                evicted_id = self._evict_lru()
                if evicted_id:
                    logger.info(f"Clock: {self.clock.get_time()}, Memory Manager, SWAP: Variable {variable_id} with Variable {evicted_id}")
            
            # Add to memory
            self.memory[variable_id] = {
                "variableId": variable_id,
                "value": disk_value,
                "lastAccessTime": self.clock.get_time()
            }
            
            # Log the Lookup operation after swap
            logger.info(f"Clock: {self.clock.get_time()}, Process {self.name.split()[-1] if ' ' in self.name else 'Unknown'}, Lookup: Variable {variable_id}, Value: {disk_value}")
            
            # Return value
            if response_queue:
                response_queue.put(disk_value)
        else:
            # Not found anywhere
            logger.info(f"Clock: {self.clock.get_time()}, Process {self.name.split()[-1] if ' ' in self.name else 'Unknown'}, Lookup: Variable {variable_id}, Not Found")
            if response_queue:
                response_queue.put(None)
  
  def _evict_lru(self):
    """
    Evict the least recently used page from memory to disk
    
    Returns:
        str: ID of the evicted variable, or None if memory was empty
    """
    if not self.is_memory_manager or not self.memory:
        return None
    
    # Find least recently used page
    lru_id = min(self.memory.keys(), key=lambda k: self.memory[k]["lastAccessTime"])
    evicted_page = self.memory.pop(lru_id)
    
    # Write to disk
    self._write_to_disk(lru_id, evicted_page["value"])
    
    return lru_id
  
  def _write_to_disk(self, variable_id, value):
    """Write a variable to disk storage"""
    if not self.is_memory_manager:
        return
        
    lines = []
    # Read existing file
    if os.path.exists(self.disk_file):
        with open(self.disk_file, 'r') as f:
            lines = f.readlines()
    
    # Update or add entry
    found = False
    for i, line in enumerate(lines):
        parts = line.strip().split(',')
        if len(parts) >= 2 and parts[0] == variable_id:
            lines[i] = f"{variable_id},{value}\n"
            found = True
            break
    
    if not found:
        lines.append(f"{variable_id},{value}\n")
    
    # Write back to file
    with open(self.disk_file, 'w') as f:
        f.writelines(lines)
  
  def _read_from_disk(self, variable_id):
    """Read a variable from disk storage"""
    if not self.is_memory_manager or not os.path.exists(self.disk_file):
        return None
    
    with open(self.disk_file, 'r') as f:
        for line in f:
            parts = line.strip().split(',')
            if len(parts) >= 2 and parts[0] == variable_id:
                return int(parts[1])
    
    return None
  
  def _remove_from_disk(self, variable_id):
    """Remove a variable from disk storage"""
    if not self.is_memory_manager or not os.path.exists(self.disk_file):
        return
    
    lines = []
    with open(self.disk_file, 'r') as f:
        for line in f:
            parts = line.strip().split(',')
            if len(parts) < 2 or parts[0] != variable_id:
                lines.append(line)
    
    with open(self.disk_file, 'w') as f:
        f.writelines(lines)


