import time, math
from thread import Thread

def readInputFile(f_path:str):
    f = open(f_path, 'r')
    contents = [s.strip() for s in f.read().splitlines()]
    time_quanta = int(contents[0])
    contents.pop(0)
    users = [(l[0], contents.index(l)) for l in contents if l[0].isalpha()]
    processes = []
    for u in users:
        number = int(contents[u[1]][-1])
        index = u[1]
        for i in range(1,1+number):
            split_contents = contents[u[1]+i]
            arrival_time = int(split_contents[0])
            service_time = int(split_contents[-1])
            processes.append((u[0], i, arrival_time, service_time))
    
    return processes, time_quanta

class Process:
    def __init__(self, arrival_Time: int, service_Time: int, user:str, p_Num: int):
        self.arrival_Time = arrival_Time
        self.service_Time = service_Time
        self.name = f"{user}, Process {p_Num}"
        # Don't Ask LOL
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
    ProcessPool = [
        # Sort Processes before creating them...
        Process(arrival_Time=p[2], service_Time=p[3], user=f"User {p[0]}", p_Num=p[1]) for p in Processes
    ]
    timeLine = 0
    scheduler = True
    while scheduler:
        process_timing = [p.arrival_Time for p in ProcessPool]
        scheduler = len(ProcessPool)!=0
        process_check = [True if p.status() == "Running" else False for p in ProcessPool]

        for p, index in zip(ProcessPool, range(len(ProcessPool))):
            if p.arrival_Time <= timeLine and p.status() not in ["Running", "Finished"]:
                if any(process_check):
                    id = process_check.index(True)
                    ProcessPool[id].stop()
                p.start()
                break
        
        ProcessPool = [p for p in ProcessPool if p.status() != "Finished"]
        time.sleep(1)
        timeLine+=1