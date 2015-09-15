#!/usr/bin/env python3

from sys import exit
import time
from modules.trace_probe.trace_probe import TraceProbe
from jobs import JobScheduler


class Node:
    """ Initialising modules and starting the main program loop """

    def __init__(self):
        """ Loading available modules and setting up logging """
        self.scheduler = JobScheduler()

    def run(self):
        """ Start the main program loop """
        try:
            while True:
                time.sleep(1)
                print("Adding traceprobe job to queue")
                self.scheduler.add(TraceProbe("213.46.237.24"))

        except KeyboardInterrupt:
            print("\nTHanks for joining!")
            exit()


def main():
    """ Main program logic called when node.py is run directly """

    node = Node()

    node.run()

if __name__ == '__main__':
    main()
