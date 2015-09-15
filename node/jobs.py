#!/usr/bin/python3

from threading import Thread
from datetime import datetime
import queue


class Job:
    """ Class describing a Job for use in the JobScheduler """
    def run(self):
        """ Runs the specified job
        each job type has to overload this function """
        pass


class JobScheduler:

    def __init__(self):
        # Create a job queue and start the scheduler in a seperate thread
        self._job_queue = queue.Queue()
        self._scheduler_thread = Thread(target=self._job_scheduler,
                                        args=(self._job_queue, ))
        self._scheduler_thread.daemon = True
        self._scheduler_thread.start()

    def __repr__(self):
        """ Print the current queue contents """
        if not self._job_queue.empty():
            return "there's stuff in the queue"
        else:
            return "Queue is empty"

    def add(self, job):
        """ Adds a new job to the queue """
        self._job_queue.put(job)

    def _job_scheduler(self, job_queue):
        while True:
            while not self._job_queue.empty():
                current_job = self._job_queue.get()
                print(current_job.run())
