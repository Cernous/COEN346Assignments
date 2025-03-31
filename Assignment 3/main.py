import time, math
from thread import Thread

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
    def __init__(self, arrival_Time: int, service_Time: int, p_Num: int):
        self.arrival_Time = arrival_Time
        self.service_Time = service_Time
        self.name = f"Process {p_Num}"
        self.__Thread = Thread(self.name, time=self.service_Time)
        self.__status = "Created"

    def start(self):
        self.__status = "Running"
        self.__Thread.start()

    def stop(self):
        self.__status = "Paused"
        self.__Thread.stop()

    def status(self):
        if self.__Thread.status()[-1] == False:
            self.__status = "Finished"
        
        return self.__status


if __name__ == "__main__":
    Processes, cores = readInputFile("Assignment 3/processes.txt")
    timeLine = 0        # Simulated TimeLine
    scheduler = True    # Active Scheduler
    readyQ = []         # Ready Queue
    CPU:Process = [None] * cores  # Current Process on the CPU if CPU is none, that means there is nothing running otherwise it is a Process
    deadLine = [0] * cores        # CPU's deadline to be compared with the timeline
    while scheduler:
        """
        There is no wrong way of programming this but only one way to achieve the near same results as the what we have in the assignment
        As long as the Processes havent been processed by the CPU or the ready queue is still not empty the scheduler will remain running
        """
        scheduler = len(Processes) != 0 or len(readyQ) != 0 or None not in CPU
        remove_indices = []
        # Creates the process depending on its arrival time
        for process in Processes:
            if process[2]*1000 == timeLine:
                # Arrival Time ding ding
                current = Process(process[1]*1000, process[2]*1000, process[10])
                remove_indices.append(Processes.index(process))
                print(f"Time {timeLine}, {current.name}, {current.status()}")
                readyQ.append(current) # Makes it available for the CPU whenever it is the first element

        # Pop elements of the processes list as they are created
        remove_indices.reverse()
        for i in remove_indices:
            Processes.pop(i)

        if None not in CPU:
            # If a process is currently on the CPU
            if any([d <= timeLine for d in deadLine]):
                # CPU Deadline ding ding
                index = CPU.index(None)
                CPU[index].stop()
                print(f"Time {timeLine}, {CPU[index].name}, {CPU[index].status()}")
                if CPU.service_Time > 0:
                    # Put back at the end of the ready queue if necessary
                    readyQ.append(CPU)
                else:
                    # Makes sures that the time allocation remains dynamic on the number of present processes
                    pass
                CPU = None
        
        """
        Putting the resume here helps with immediately assigning something instead of waiting another second
        """
        if len(readyQ) > 0 and None in CPU:
            # If the CPU is waiting for a process to run while something still lurks on the ready queue
            index = CPU.index(None)
            CPU[index] = readyQ.pop(0)
            CPU[index].start()
            print(f"Time {timeLine}, {CPU[index].name}, {CPU[index].status()}")
            deadLine[index] = CPU[index].arrival_Time + CPU[index].service_Time
        
        time.sleep(0.001)
        timeLine += 1