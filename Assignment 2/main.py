import time, math
from thread import Thread

def readInputFile(f_path:str):
    """
    Takes in a file path and opens it to read its specific format to then create the parameters for the processes
    First line is always the time quantum of the system followed by its users and the processes
    """
    f = open(f_path, 'r')
    contents = [s.strip() for s in f.read().splitlines()]
    time_quanta = int(contents[0])
    contents.pop(0)         # time quantum
    # Sort by Users
    users = [(l[0], contents.index(l)) for l in contents if l[0].isalpha()] 
    processes = []
    # Sort by Processes
    for u in users:
        number = int(contents[u[1]][-1])
        index = u[1]
        for i in range(1,1+number):
            # If the given number does not correspond to the number of lines that follows this procedure will fail
            split_contents = contents[u[1]+i]
            arrival_time = int(split_contents[0]) # Failure will happen here if there is a user immediately after the scanned one
            service_time = int(split_contents[-1])
            processes.append((u[0], i, arrival_time, service_time))
    
    return processes, time_quanta

class Process:
    """
    Process Class contains specific parameters and properties that control the status of a 'process'
    while also having a Thread to simulate its run time on the CPU

    Status's are dependent on the threads properties and NOT its own property for authenticity
    so even if the process is being juggled around, the status cannot be manipulated outside of its own class
    """
    def __init__(self, arrival_Time: int, service_Time: int, user:str, p_Num: int):
        self.arrival_Time = arrival_Time
        self.service_Time = service_Time
        self.user = user
        self.name = f"{user}, Process {p_Num}"
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
    Processes, timequant = readInputFile("Assignment 2/input.txt")
    timeLine = 0        # Simulated TimeLine
    scheduler = True    # Active Scheduler
    readyQ = []         # Ready Queue
    CPU:Process = None  # Current Process on the CPU if CPU is none, that means there is nothing running otherwise it is a Process
    deadLine = 0        # CPU's deadline to be compared with the timeline
    users = {}          # Used for time allocation for each process and CPU
    while scheduler:
        """
        There is no wrong way of programming this but only one way to achieve the near same results as the what we have in the assignment
        As long as the Processes havent been processed by the CPU or the ready queue is still not empty the scheduler will remain running
        """
        scheduler = len(Processes) != 0 or len(readyQ) != 0 or CPU is not None
        remove_indices = []
        # Creates the process depending on its arrival time
        for process in Processes:
            if process[2] == timeLine:
                # Arrival Time ding ding
                current = Process(process[2], process[3], f"User {process[0]}", process[1])
                remove_indices.append(Processes.index(process))
                print(f"Time {timeLine}, {current.name}, {current.status()}")
                readyQ.append(current) # Makes it available for the CPU whenever it is the first element
                # Makes sures that the time allocation remains dynamic on the number of present processes
                if f"User {process[0]}" in users:
                    users[f"User {process[0]}"].append(current.name)
                else:
                    users[f"User {process[0]}"] = [current.name]

        # Pop elements of the processes list as they are created
        remove_indices.reverse()
        for i in remove_indices:
            Processes.pop(i)

        if CPU is not None:
            # If a process is currently on the CPU
            if deadLine == timeLine:
                # CPU Deadline ding ding
                CPU.stop()
                print(f"Time {timeLine}, {CPU.name}, {CPU.status()}")
                if CPU.service_Time > 0:
                    # Put back at the end of the ready queue if necessary
                    readyQ.append(CPU)
                else:
                    # Makes sures that the time allocation remains dynamic on the number of present processes
                    users[CPU.user].remove(CPU.name)
                CPU = None
        
        """
        Putting the resume here helps with immediately assigning something instead of waiting another second
        """
        if len(readyQ) > 0 and CPU is None:
            # If the CPU is waiting for a process to run while something still lurks on the ready queue
            CPU = readyQ.pop(0)
            CPU.start()
            print(f"Time {timeLine}, {CPU.name}, {CPU.status()}")
            timeallocated = int(timequant / (len(users.keys()) * len(users[CPU.user])))
            deadLine = timeLine + (timeallocated if CPU.service_Time >= timeallocated else CPU.service_Time)
            # Manipulate the remaining service time to sync with the thread
            CPU.service_Time = CPU.service_Time - timeallocated if CPU.service_Time - timeallocated >= 0 else 0
        
        time.sleep(1)
        timeLine +=1