#!/usr/bin/python

import threading
from time import sleep

def multithreadrun(function, arg_list, thread):
    threads = []
    len_arg = len(arg_list)
    range_arg = range(len_arg)
    for i in range_arg:
        t = threading.Thread(target = function, args = arg_list[i])
        threads.append(t)
        
    i = 0
    while i < len_arg:
        if int(threading.activeCount()) <= int(thread):
            threads[i].start()
            i = i + 1
        else:
            sleep(1)
    for i in threads:
        i.join()

#l = [(1,),(2,),(3,),(4,),(5,),(6,),(7,),(8,)]

#def a(a):
#    sleep(a)
#    print a

#multithreadrun(a, l, 1)

