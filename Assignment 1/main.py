import math
from thread import Thread
from functools import partial

def checkNumFormat(input:str):
    if input.isdigit():
        return int
    elif input.count(".") == 1 and input.replace(".", "").isdigit():
        return float
    else:
        return str
    
def toBinary(num: int) -> str:
    binlist = []
    while num >= 1:
        binlist.append(str(num%2))
        num = math.floor(num/2)
    return "".join(reversed(binlist))

def merge(left:list, right:list):
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
    if len(arr)==1:
        return arr
    
    mid = len(arr)//2
    left_half =  mergeSort(arr[:mid])
    right_half = mergeSort(arr[mid:])

    return merge(left_half, right_half)

def mergeSort(arr:list, threadNum: int):
    if len(arr)==1:
        return arr
    
    mid = len(arr)//2
    left_half =  mergeSort(arr[:mid], threadNum+1)
    right_half = mergeSort(arr[mid:], threadNum+2)

    return Thread(f"Thread {toBinary(threadNum)}", partial(merge, left_half, right_half)).run()

if __name__ == "__main__":
    f = open('Assignment 1/input.txt', 'r')
    input_contents = [line.strip().replace(",", "") for line in f.readlines()]
    threadpool: list[Thread] = []
    input_contents = [checkNumFormat(cont)(cont) for cont in input_contents]
    print(Thread(f"Thread {toBinary(1)}", partial(mergeSort,input_contents,1)).run())