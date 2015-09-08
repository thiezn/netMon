#!/usr/bin/env python

import time
from datetime import datetime

class Job:
    """ A Job that can be scheduled by the JobHandler class """

    def __init__(self, job_name="Job Doe"):
        self.interval = None    # Run every <interval> seconds
        self.last_run = None
        self.next_run = None
        self.job_name = job_name

    def run(self):
        print("%s Running job %s" % (self.last_run, self.job_name))


class JobHandler:
    """ Class that handles scheduled jobs """

    def __init__(self):
        """ Loading available modules and setting up logging """
        self.jobs = []

    def add(self, job, run_at):
        """ Add a job to the queue """
        self.jobs.append(job)

    def run(self):
        while True:
            for job in self.jobs:
                job.last_run = datetime.now()
                job.run()
                time.sleep(1)
