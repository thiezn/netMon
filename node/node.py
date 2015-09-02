#!/usr/bin/env python

from modules.icmp_probe.icmp_probe import IcmpProbe


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
    icmp_probe.run()
    icmp_probe.stop()
    print icmp_probe.avg

if __name__ == '__main__':
    main()
