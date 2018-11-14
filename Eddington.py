#File: Eddington.py

from functools import reduce

def edNum(listOfNumbers):
    listOfNumbers.sort()
    listOfNumbers.reverse()
    rank = 1
    previous = 0
    for l in listOfNumbers:
    #    print("%f -> Rank: %f" % (l,rank))
        if rank > l:
            return rank-1
        rank += 1
        previous = l
    return l
