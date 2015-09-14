#!/usr/bin/python

from threading import Thread
import Queue


class Job:
    """ Class describing a Job for use in the JobScheduler """
    def __init__(self):
        pass

    def run(self):
        """ Runs the specified job
        each job type has to overload this function """
        pass


class JobScheduler:

    def __init__(self):
        self._job_queue = Queue.Queue()
        self._scheduler_thread = Thread(target=self._job_scheduler,
                                        args=(self._job_queue, ))
        self._scheduler_thread.daemon = True
        self._scheduler_thread.start()

    def add(self, job):
        """ Adds a new job to the queue """
        self._job_queue.put(job)

    def _job_scheduler(self, job_queue):
        while True:
            while not self._job_queue.empty():
                current_job = self._job_queue.get()
                result = current_job.run()
                print result
