import time, math
from thread import Thread
from functools import partial
from commands_memconfig import *
from memory_disk import *

def readInputFile(f_path:str):
    """
    Takes in a file path and opens it to read its specific format to then create the parameters for the processes
    First line is always the number of cores of the system followed by the processes
    """
    f = open(f_path, 'r')
    contents = [s.strip() for s in f.read().splitlines()]
    core = int(contents.pop(0)) # number of cores
    processes = []
    # Sort by Processes
    for p in range(int(contents.pop(0))):
        # If the given number does not correspond to the number of lines that follows this procedure will fail
        split_contents = contents[p]
        arrival_time = int(split_contents[0]) # Failure will happen here if there is a user immediately after the scanned one
        service_time = int(split_contents[-1])
        processes.append((p, arrival_time, service_time))
    
    return processes, core

class Process:
    """
    Process Class contains specific parameters and properties that control the status of a 'process'
    while also having a Thread to simulate its run time on the CPU

    Status's are dependent on the threads properties and NOT its own property for authenticity
    so even if the process is being juggled around, the status cannot be manipulated outside of its own class
    """
    def __init__(self, MemObj: Memory_Disk, arrival_Time: int, service_Time: int, p_Num: int):
        self.arrival_Time = arrival_Time
        self.service_Time = service_Time
        self.mem_Object = MemObj
        self.name = f"Process {p_Num}"
        self.__Thread = Thread(self.name, time=self.service_Time)
        self.__status = "Created"

    def start(self):
        self.__status = "Running"
        self.__Thread.start()

    def stop(self):
        self.__status = "Finished"
        self.__Thread.stop()

    def status(self):
        temp = self.__Thread.status()
        if temp[1] == False:
            self.__status = "Finished"
        else:
            self.__status = "Running" if temp[-1] else "Idling"
        
        return self.__status
    
    def assign(self, command:list):
        partial_Obj = None
        match(command[0].lower()):
            case "store":
                partial_Obj = partial(self.mem_Object.store, id=command[1], value=command[2])
            case "lookup":
                partial_Obj = partial(self.mem_Object.lookup, id=command[1])
            case "release":
                partial_Obj = partial(self.mem_Object.release, id=command[1])
        
        if partial_Obj is not None and self.__status == "Idling":
            self.__Thread.assign(partial_Obj, command)

"""
Scheduler - Yes in Main
"""
DEBUG = True
if __name__ == "__main__":
    Processes, cores = readInputFile("Assignment 3/processes.txt")
    commands = readCommandsFile("Assignment 3/commands.txt")
    memconfig = readMemConfigFile("Assignment 3/memconfig.txt")
    initial_Processes = list(Processes)
    initial_Commands = list(commands)
    start = round(time.time() * 1000)
    Memory_Object = Memory_Disk(memconfig, start)
    
    timeLine = 0        # True TimeLine (changed for time.time() timestamps for full process synchronization later)
    scheduler = True    # Active Scheduler
    readyQ = []         # Ready Queue
    CPU:list[Process] = [None] * cores  # Current Process on the CPU if CPU is none, that means there is nothing running otherwise it is a Process
    deadLine = [0] * cores        # CPU's deadline to be compared with the timeline
    while scheduler:
        """
        There is no wrong way of programming this but only one way to achieve the near same results as the what we have in the assignment
        As long as the Processes havent been processed by the CPU or the ready queue is still not empty the scheduler will remain running
        """
        scheduler = len(Processes) != 0 or len(readyQ) != 0 or not all([p == None for p in CPU])
        remove_indices = []
        # Creates the process depending on its arrival time
        for process in Processes:
            if process[1]*1000 == timeLine:
                # Arrival Time ding ding
                current = Process(Memory_Object, process[1]*1000, process[2]*1000, process[0])
                remove_indices.append(Processes.index(process))
                print(f"Time {timeLine}, {current.name}, {current.status()} and Appended to the Ready Queue")
                readyQ.append(current) # Makes it available for the CPU whenever it is the first element

        # Pop elements of the processes list as they are created
        remove_indices.reverse()
        for i in remove_indices:
            Processes.pop(i)

        """
        Process termination for deadline met or overdue
        """
        if any([isinstance(p, Process) for p in CPU]):
            # If a process is currently on the CPU
            if any([d <= timeLine and d != 0 for d in deadLine]):
                # CPU Deadline ding ding
                index = [d <= timeLine for d in deadLine].index(True)
                CPU[index].stop()
                print(f"Time {timeLine}, {CPU[index].name}, CPU {index}, {CPU[index].status()}")
                if CPU[index].service_Time > 0:
                    # Not being used since - Assignment 2
                    # Put back at the end of the ready queue if necessary
                    readyQ.append(CPU[index])
                else:
                    # No more dynamic time allocation per user process
                    pass

                # Destroy processes when done
                CPU[index] = None
                deadLine[index] = 0

                # # Loop mechanism - Assignment 3
                # if all([p == None for p in CPU]) and len(Processes) == 0:
                #     Processes = list(initial_Processes)
                #     Processes = [(p[0], p[1] + timeLine/1000, p[2]) for p in Processes]

            """
            Command Assignment of the Processes
            """
            # Precision is not really of concern if we are counting per milliseconds
            # Need to see what is A running but idle process
            for p,i in zip(CPU, range(cores)):
                if isinstance(p, Process):
                    if p.status() == "Idling" and len(commands) != 0:
                        c = commands.pop(0)
                        p.assign(c)
                        print(f"Time {timeLine}, {p.name}, CPU {i}, {p.status()} {c}")
                
        
        """
        Putting the resume here helps with immediately assigning something instead of waiting another second
        """
        if len(readyQ) > 0 and None in CPU:
            # If the CPU is waiting for a process to run while something still lurks on the ready queue
            index = CPU.index(None)
            CPU[index] = readyQ.pop(0)
            CPU[index].start()
            print(f"Time {timeLine}, {CPU[index].name}, CPU {index}, {CPU[index].status()}")
            deadLine[index] = CPU[index].arrival_Time + CPU[index].service_Time
            CPU[index].service_Time = 0 # prevents the readdition of the process unto the ReadyQ
        
        time.sleep(0.001)
        timeLine = (round(time.time() * 1000) - start) if not DEBUG else timeLine + 1

    print("Scheduler Done!")
    Memory_Object.printmem()
    Memory_Object.printdisk()
