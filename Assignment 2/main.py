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
        self.user = user
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

    timeperuser = timequant
    processblock = []

    cyclestart = timeLine
    cycleend = timeLine+timequant

    while scheduler:
        scheduler = len(ProcessPool)!=0
        process_check = [True if p.status() == "Running" else False for p in ProcessPool]

        

        if timeLine == cycleend or cyclestart == 0:
            
            if cyclestart != 0:
                for process in processblock:
                    if process.status() == "Running":
                        process.stop()
            cyclestart = timeLine
            cycleend = cyclestart + timequant

            print("Start: " + str(cyclestart))

            for p, index in zip(ProcessPool, range(len(ProcessPool))):
                if p.arrival_Time <= timeLine and p.status() not in ["Running", "Finished"]:
                    if p not in processblock:
                        processblock.append(p)

            processesperuser = {}

            for p in processblock:
                if p.user not in processesperuser:
                    processesperuser[p.user] = 0

            for p in processblock:
                if p.status() == "Finished":
                    processblock.remove(p)

            for process in processblock:
                for user in processesperuser:
                    if process.user == user:
                        processesperuser[user] += 1

            processtimeallotted = {}

            for process in processblock:
                timeallotted = timequant/(len(processesperuser)*processesperuser[process.user])
                processtimeallotted[process] = timeallotted

            processtimings = {}

            timestart = cyclestart
            timefinish = cyclestart
            for process in processtimeallotted:
                timefinish = timefinish + processtimeallotted[process]
                processtimings[process] = [timestart,timefinish]
                timestart = timefinish

        if timeLine <= 1:
            for process in processtimings:
                if timeLine == processtimings[process][0]:
                    process.start()
                elif timeLine == processtimings[process][1]:
                    process.stop()

        
        for process in processblock:
            print(str(timeLine) + " " + process.name + " " + process.status())
        for process in processtimings:
            print(processtimings[process])
        # for key in processtimings:
        #     print(key, processtimings[key])
        # print(len(processblock))

        # for p, index in zip(ProcessPool, range(len(ProcessPool))):
        #     if p.arrival_Time <= timeLine and p.status() not in ["Running", "Finished"]:
        #         if any(process_check):
        #             id = process_check.index(True)
        #             ProcessPool[id].stop()
        #         p.start()
        #         running_process = p
        #         running_start_time = timeLine
        #         break
        

        
        ProcessPool = [p for p in ProcessPool if p.status() != "Finished"]
        time.sleep(1)
        timeLine+=1