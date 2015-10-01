#!/usr/bin/env python3

from tasks import Task


class IcmpProbe(Task):
    """ Runs an ICMP probe to the provided destination """

    def __init__(self, dest_addr):
        super().__init__()
        self.dest_addr = dest_addr

    def run(self):
        print("Running ping to {}".format(self.dest_addr))
