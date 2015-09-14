#!/usr/bin/env python

import time
from modules.icmp_probe.icmp_probe import IcmpProbe
from modules.trace_probe.trace_probe import TraceProbe
from jobs import JobScheduler


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
    trace_probe = TraceProbe("213.46.237.24")

    print icmp_probe.run()
    print trace_probe.run()

    scheduler = JobScheduler()
    for i in range(10):
        time.sleep(1)
        print("Adding job to job queue")
        scheduler.add(icmp_probe)
        scheduler.add(trace_probe)


if __name__ == '__main__':
    main()
