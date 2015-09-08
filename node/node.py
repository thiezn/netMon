#!/usr/bin/env python

from modules.icmp_probe.icmp_probe import IcmpProbe
from modules.trace_probe.trace_probe import TraceProbe
from job_handler import Job, JobHandler

class Node:
    """ Initialising modules and starting the main program loop """

    def __init__(self):
        """ Loading available modules and setting up logging """
        pass

    def run(self):
        """ Start the main program loop """
        pass


def main():
    """ Main program logic called when node.py is run directly """
    icmp_probe = IcmpProbe("10.0.0.1")
    print icmp_probe.run()

    trace_probe = TraceProbe("213.46.237.24")
    print trace_probe.run()

    job = Job()
    job_handler = JobHandler()

    job_handler.add(job, "now")
    job_handler.run()

if __name__ == '__main__':
    main()
