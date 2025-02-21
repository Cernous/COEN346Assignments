import time, math
from thread import Thread

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
    ProcessPool = [
        # Sort Processes before creating them...
        Process(1,10,"User A", 1),
        Process(5,12,"User A", 2)
    ]
    timeLine = 0
    timequant = 4           # Not implemented
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
        


    