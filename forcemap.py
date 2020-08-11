'''
Like dummy.Pool.map, but no limit of number of threads. 
Useful when IO-bound. 
'''
from threading import Thread, Lock, Condition
from queue import Queue

def forceMap(function, iter_input, thread_max = 4):
    thread_num = 0
    result_num = 0
    list_output = [None] * len(iter_input)
    queue = Queue()
    for i, input in enumerate(iter_input):
        if thread_num < thread_max:
            thread_num += 1
            MyThread(i, input, function, queue)
        else:
            id, output = queue.get()
            list_output[id] = output
            result_num += 1
            MyThread(i, input, function, queue)
    while result_num < len(list_output):
        id, output = queue.get()
        list_output[id] = output
        result_num += 1
    return list_output

class MyThread(Thread):
    def __init__(self, id, input, function, queue):
        super(__class__,self).__init__()
        self.id = id
        self.input = input
        self.function = function
        self.queue = queue
        self.start()
    
    def run(self):
        output = self.function(self.input)
        self.queue.put((self.id, output))

if __name__ == '__main__':
    from time import sleep
    
    def task(name):
        print(name,'start')
        sleep(.5)
        print(name, 1)
        sleep(.5)
        print(name, 2)
        sleep(.5)
        print(name, 'END')
        return name
    
    print(forceMap(task,range(9),9))
    input('EENNDD\n')
