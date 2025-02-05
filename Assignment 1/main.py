import math
from thread import Thread
from functools import partial

def checkNumFormat(input:str):
    """
    Outputs the correct format given a string
    """
    if input.isdigit():
        return int
    elif input.count(".") == 1 and input.replace(".", "").isdigit():
        return float
    else:
        return str
    
def toBinary(num: int) -> str:
    """
    Turns a integer into a binary number
    """
    binlist = []
    while num >= 1:
        binlist.append(str(num%2))
        num = math.floor(num/2)
    return "".join(reversed(binlist))

def merge(left:list, right:list):
    """
    Merge function that sorts 2 lists based on their contents and merges them
    """
    merged = []
    i = 0
    j = 0
    if left is None or right is None:
        return
    while i < len(left) and j < len(right):
        if left[i] < right[j]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1

    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged

def mergeSort(arr: list):
    """
    Original MergeSort function
    """
    if len(arr)==1:
        return arr
    
    mid = len(arr)//2
    left_half =  mergeSort(arr[:mid])
    right_half = mergeSort(arr[mid:])

    return merge(left_half, right_half)

def mergeSort(arr:list, threadPool: list[Thread]):
    """
    MergeSort with Threads, using threadpool for further debugging as the threads join by themselves after running
    """
    if len(arr)==1:
        return arr
    
    mid = len(arr)//2

    tleft = Thread(f"Thread {toBinary(len(threadPool)+1)}", partial(mergeSort, arr[:mid], threadPool))
    threadPool.append(tleft)
    left_half = tleft.run()

    tright = Thread(f"Thread {toBinary(len(threadPool)+1)}", partial(mergeSort, arr[mid:], threadPool))
    threadPool.append(tright)
    right_half = tright.run()
    
    return merge(left_half, right_half)

if __name__ == "__main__":
    f = open('Assignment 1/input.txt', 'r')
    input_contents = [line.strip().replace(",", "") for line in f.readlines()]
    threadpool: list[Thread] = []
    input_contents = [checkNumFormat(cont)(cont) for cont in input_contents]
    threadpool.append(Thread(f"Thread {toBinary(1)}", partial(mergeSort,input_contents, threadpool)))
    print(threadpool[0].run())
    try:
        for t in threadpool:
            t.join()
    except Exception as e:
        print(e)