#!/usr/bin/env python3

from sys import exit
import time
from modules.trace_probe.trace_probe import TraceProbe
from jobs import JobScheduler
from libs.network import NodeControllerClient

class Node:
    """ Initialising modules and starting the main program loop """

    def __init__(self):
        """ Loading available modules and setting up logging """
        self.scheduler = JobScheduler()
        self.node_controller = NodeControllerClient('127.0.0.1', 10666)

        self.node_controller.register()

    def run(self):
        """ Start the main program loop """
        try:
            while True:
                # This is where we will be responding to events like:

                # if not connected to supernode: Connect to supernode
                # if request for new probe is received: add new probe to queue
                # if request for shutdown received: shutdown gracefully
                time.sleep(1)
                print("Adding traceprobe job to queue")
                self.scheduler.add(TraceProbe("213.46.237.24"))
                self.node_controller.probe_result({'type': 'probe', 'probe_type': 'icmp', 'result': 1})

        except KeyboardInterrupt:
            print("\nTHanks for joining!")
            exit()

def main():
    """ Main program logic called when node.py is run directly """

    node = Node()
    node.run()

if __name__ == '__main__':
    main()
