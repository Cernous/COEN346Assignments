from thread import ThreadC

def checkNumFormat(input:str):
    if input.isdigit():
        return int
    elif input.count(".") == 1 and input.replace(".", "").isdigit():
        return float
    else:
        return str
    

def merge(left:list, right:list):
    merged = []
    i = 0
    j = 0

    while i < len(left) and j < len(right):
        if left[i] < right[j]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1

    merged.extend


def mergeSort(arr: list):
    if len(arr):
        return arr
    
    mid = len(arr)//2
    left_half = mergeSort(arr[:mid])
    right_half = mergeSort(arr[mid:])

    return merge(left_half, right_half)

if __name__ == "__main__":
    f = open('Assignment 1/input.txt', 'r')
    input_contents = [line.strip().replace(",", "") for line in f.readlines()]
    threadpool: list[ThreadC] = []
    input_contents = [checkNumFormat(cont)(cont) for cont in input_contents]
    print(input_contents)
    pass