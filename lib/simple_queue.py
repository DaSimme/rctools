""" queue.py: adapted from uasyncio V2
# Copyright (c) 2018-2020 Peter Hinch
# Released under the MIT License (MIT) - see LICENSE file
# Code is based on Paul Sokolovsky's work.
# This is a temporary solution until uasyncio V3 gets an efficient official version
# Origin: https://github.com/peterhinch/micropython-async/blob/master/v3/primitives/queue.py
Changes for RC-Tools by Simeon Hiertz.
"""
# Exception raised by get_nowait().
class QueueEmpty(Exception):
    """Raises an error when the queue is empty."""
    pass


# Exception raised by put_nowait().
class QueueFull(Exception):
    """Raises an error when the queue is full."""
    pass

class Queue:
    """Main Queue class, simplified for RC-usecases."""
    def __init__(self, maxsize=100):
        self.maxsize = maxsize #Default size for measurements is 100 values
        self._queue = []

    def get(self):
        """Retrieve an the first in element."""
        if self.empty():
            raise QueueEmpty()
        return self._queue.pop(0)

    def put(self, val):
        """Put item in queue, delete last elemt if necessary."""
        if self.full():
            self._queue.pop(0)
        self._queue.append(val)

    def qsize(self):   
        """Number of items in the queue."""
        return len(self._queue)

    def empty(self):
        """Return True if the queue is empty, False otherwise."""
        return len(self._queue) == 0

    def full(self):
        """Return True if there are maxsize items in the queue.
        Note: if the Queue was initialized with maxsize=0 (the default) or
        any negative number, then full() is never True."""
        return self.maxsize > 0 and self.qsize() >= self.maxsize
    
    def get_avg(self):
        """Returns the average of all elements in queue."""
        x_int:int=0
        x_float:float=0
        if isinstance(self._queue[0],int):
            x_int=sum(self._queue)//len(self._queue)
            return x_int
        else:
            x_float=sum(self._queue)/len(self._queue)
            return x_float
    

if __name__=="__main__":
    q1=Queue(5)
    q1.put(20)
    q1.put(22)
    q1.put(30)
    q1.put(22)
    q1.put(10)
    q1.put(100)
    q1.get_avg()
