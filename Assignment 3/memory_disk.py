import time, math
from thread import Thread

class Memory_Disk:
    """
    Memory_Disk class contains the memory and the hard disk. The store, lookup, and release functions are located in here.
    """
    memory_size = 0
    memory = []
    disk = []
    time = time.time()

    def __init__(self):
        pass

    def __init__(self, memsize):
        self.memory_size = memsize
        self.memory [None]*memsize

    def updateTime(self, start): #Updates the current time within the class
        self.time = time.time() - start

    def updateLastAccess(self, value): #Updates the last accessed time in an id, value pair.
        value[2] = self.time

    def memFreeSlots(self): #Checks how many free slots there are in the memory and returns it.

        count = self.memory_size
        for i in range(len(self.memory)):
            if self.memory[i] == None:
                count += 1

        return count

    def lookupMemory(self, id): #Searches for a value by id within the memory.
        for i in range(len(self.memory)):
            if id == self.memory[i][0]:
                return i #Returns the index at which the id was found
        
        return -1 #Returns -1 if the id was not found
    
    def lookupDisk(self, id): #Searches for a value by id within the disk.
        for i in range(len(self.disk)):
            if id == self.disk[i][0]:
                return i #Returns the index at which the id was found
        
        return -1 #Returns -1 if the id was not found

    def store(self, id, value): #Stores an id value pair as a  into the first unassigned spot in the memory. Returns True if a memory slot is open and False if there are no free memory slots.
        self.updateTime()

        if self.memFreeSlots() < 0: #If memory is NOT full
            for i in range(len(self.memory)):
                if self.memory[i] == None: #Store at the first available slot
                    self.memory[i] == [id, value, self.time]
                    break
            return True
        
        else:
            return False

    def release(self, id): #Releases an id-value pair from the memory and returns the tuple (id, value). Returns -1 if it does not exist.
        self.updateTime()

        index = self.lookupMemory(id)

        if index != -1: #Check if the id currently exists in the memory
            self.updateLastAccess(self.memory[index])
            idvalue = self.memory[index]
            self.memory[index] = None
            return idvalue
        else:
            return -1

    def lookup(self, id):

            

