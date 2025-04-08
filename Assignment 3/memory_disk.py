import time, math
from thread import Thread
import datetime as dt
import logging
from multiprocessing import Semaphore, Lock

logging.basicConfig(
    filename="Assignment 3/output.txt", level=logging.INFO, filemode="w"
)
vmfile = "Assignment 3/virtual_memory.txt"

logger = logging.getLogger()

RELEASEMODE: bool = False

class Memory_Disk:
    """
    Memory_Disk class contains the memory and the hard disk. The store, lookup, and release functions are located in here.
    Data structure for variables that will be stored in memory or disk are lists.

    [id, value, time last accessed]
    """
    start = 0
    memory_size = 0
    memory = []
    disk = []
    time = 0

    #Semaphors
    empty = Semaphore(memory_size)
    full = Semaphore(0)
    mutex = Lock()

    def __init__(self):
        pass

    def __init__(self, memsize, starttime):
        self.memory_size = memsize
        self.memory = [None]*memsize
        self.empty = Semaphore(memsize)
        self.start = starttime
        try:
            self.virtual_mem = open(vmfile, 'r')
            self.disk = [[int(j) if i == len(l.split('\t'))-1 else j for j, i in zip(l.split("\t"), range(len(l.split("\t"))))] for l in self.virtual_mem.readlines()]
            self.virtual_mem.close()
        except:
            pass

    def updateTime(self): #Updates the current time within the class
        self.time = round(time.time()*1000) - self.start

    def updateLastAccess(self, value): #Updates the last accessed time in an id, value pair.
        value[2] = self.time

    def memFreeSlots(self): #Checks how many free slots there are in the memory and returns it.

        count = 0
        for i in range(len(self.memory)):
            if self.memory[i] == None:
                count = count + 1

        return count

    def lookupMemory(self, id): #Searches for a value by id within the memory.
        for i in range(len(self.memory)):
            if self.memory[i] != None:
                if id == self.memory[i][0]:
                    return i #Returns the index at which the id was found
        
        return -1 #Returns -1 if the id was not found
    
    def lookupDisk(self, id): #Searches for a value by id within the disk.
        for i in range(len(self.disk)):

            if id == self.disk[i][0]:
                return i #Returns the index at which the id was found
        
        return -1 #Returns -1 if the id was not found
    
    def leastRecent(self): #Method that returns the id of the least recently accessed variable id in the memory
        accesstimes = {}

        for i in range(len(self.memory)):
            if self.memory[i] != None:
                accesstimes[i] = self.memory[i][2]
        
        return self.memory[min(accesstimes, key=accesstimes.get)][0]

    def storehelper(self, id, value): #Stores an id value pair as a  into the first unassigned spot in the memory. Returns True if a memory slot is open and False if there are no free memory slots.
        self.updateTime()

        if self.memFreeSlots() > 0: #If memory is NOT full
            for i in range(len(self.memory)):
                if self.memory[i] == None: #Store at the first available slot
                    self.memory[i] = [id, value, self.time]
                    break
            return True
        
    def releasehelper(self, id): #Releases an id-value pair from the memory and returns the id, value list. Returns -1 if it does not exist.
        index = self.lookupMemory(id)

        if index != -1: #Check if the id currently exists in the memory
            # self.updateLastAccess(self.memory[index])
            idvalue = self.memory[index]
            self.memory[index] = None
            return idvalue
        else:
            return -1

    """
    APIs - These are the actual API methods that can be called by the processes.
    """
    def store(self, id, value): #Stores an id value pair as a  into the first unassigned spot in the memory. Returns True if a memory slot is open and False if there are no free memory slots.

        self.mutex.acquire()
        
        self.updateTime()

        # Critical section
        
        if self.memFreeSlots() == 0: # If memory is FULL, store into disk
            try:
                if len(self.disk) == 0 or not any([id == mem[0] for mem in self.disk]):
                    self.disk.append([id, value, self.time])
                else:
                    self.disk = [[id, value, self.time] if id == mem[0] else mem for mem in self.disk]
                self.diskhelper()
                output = False
            finally:
                self.mutex.release()
        
        else: # If memory is NOT FULL
        
            self.empty.acquire()
            try:
                for i in range(len(self.memory)):
                    if self.memory[i] == None: #Store at the first available slot
                        self.memory[i] = [id, value, self.time]
                        break
                output = True
                
            finally:
                self.mutex.release()
        return output
    



    def release(self, id): #Releases an id-value pair from the memory and returns the id, value list. Returns -1 if it does not exist.
        if RELEASEMODE:
            """
            This release() will release a variable from memory ONLY. If it's in the disk, it will return -1.
            """
            self.mutex.acquire()
            try:
                index = self.lookupMemory(id)

                if index != -1: #Check if the id currently exists in the memory
                    # self.updateLastAccess(self.memory[index])
                    idvalue = self.memory[index]
                    self.memory[index] = None

                    self.empty.release()
                    output = idvalue
                else:
                    output = -1
            finally:
                self.mutex.release()
        
            return output
        
        else:
            """
            This is the version of release() which will release a variable id from disk if it's not in memory.
            """
            
            self.mutex.acquire()
            try:

                if self.lookupMemory(id) != -1: #Check if the id currently exists in the memory
                    index = self.lookupMemory(id)
                    idvalue = self.memory[index]
                    self.memory[index] = None

                    self.empty.release()
                    output = idvalue
                elif self.lookupDisk(id) != -1: #Check if the id currently exists in the disk
                    index = self.lookupDisk(id)
                    idvalue = self.disk.pop(index)

                    output = idvalue
                    self.diskhelper()
                else:
                    output = -1
            finally:
                self.mutex.release()
            
            return output

    def lookup(self, id):
        self.mutex.acquire()
        self.updateTime()
        try:
            #Check if id is in the memory
            memindex = self.lookupMemory(id)
            if memindex != -1: #If the id is in the memory, update its last accessed time and returns the value associated to the id
                self.memory[memindex][2] = self.time
                output = self.memory[memindex][1]
                
            elif self.lookupDisk(id) != -1: #if id is in the disk, attempt to load the variable into memory
                diskindex = self.lookupDisk(id)
                if self.memFreeSlots() > 0: #If there is free space in the memory
                    self.full.acquire()
                    try:
                        #Moves the id variable from the disk into the memory and updates its last accessed time
                        self.disk[diskindex][2] = self.time #update last accessed time
                        output = self.disk[diskindex][1]
                        self.storehelper(self.disk[diskindex][0], self.disk[diskindex][1])
                        del self.disk[diskindex]
                        self.diskhelper()
                    finally:
                        self.empty.release()

                else: #If there is not free space in the memory

                    #Swaps the least recently accessed id in memory with the given id and updates last accesed time

                    leastrecent = self.releasehelper(self.leastRecent())
                    self.storehelper(self.disk[diskindex][0], self.disk[diskindex][1])
                    self.disk[diskindex][2] = self.time #update time
                    output = self.disk[diskindex][1]
                    logger.info(
                        " ".join(
                            [
                                f"[{dt.datetime.now().strftime('%H:%M:%S')}]: ",
                                f"Memory Disk Manager Swap: ID {self.disk[diskindex][0]} with ID {leastrecent[0]}",
                            ]
                        )
                    )
                    del self.disk[diskindex]
                    self.disk.append(leastrecent)
                    self.diskhelper()

            else: output = -1
        
        finally:
            self.mutex.release()
            return output
    
    def printmem(self):
        toprint = "Memory Contents\n"
        for i in range(len(self.memory)):
            if self.memory[i] == None:
                print("None")
            else:
                toprint += str(self.memory[i][0]) + " | " + self.memory[i][1] + " | " + str(self.memory[i][2]) + "\n"
                
        toprint += "\n"
        print(toprint)
    
    def printdisk(self):
        toprint = "Disk Contents\n"
        for i in range(len(self.disk)):
            toprint += str(self.disk[i][0]) + " | " + self.disk[i][1] + " | " + str(self.disk[i][2]) + "\n"
        toprint += "\n"
        print(toprint)

    def diskhelper(self):
        self.virtual_mem = open(vmfile, 'w')
        output = "\n".join(["\t".join([mem[0], mem[1], str(mem[2])]) for mem in self.disk])
        self.virtual_mem.write(output)
        self.virtual_mem.close()

            
"""
Test
"""
if __name__ == "__main__":        
    myobj = Memory_Disk(2,0)

    myobj.store(1, 'value of 1')
    myobj.store(2, 'value of 2')
    myobj.store(3, 'value of 3')
    myobj.store(4, 'value of 4')
    myobj.store(5, 'value of 5')
    myobj.store(6, 'value of 6')

    myobj.lookup(5)

    myobj.printmem()
    myobj.printdisk()