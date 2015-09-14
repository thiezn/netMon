#!/usr/bin/python

import time
from threading import Thread
import Queue


def job_scheduler(job_queue):
    time.sleep(5)
    while not job_queue.empty():
        print(job_queue.get())
        time.sleep(1)

job_queue = Queue.Queue()

job_scheduler_thread = Thread(target=job_scheduler, args=(job_queue, ))
job_scheduler_thread.start()

for i in range(10):
    time.sleep(1)
    print("Adding job to job queue")
    job_queue.put("Hello World")
