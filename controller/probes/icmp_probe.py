#!/usr/bin/env python3

from tasks import Task


class IcmpProbe(Task):
    """ Runs an ICMP probe to the provided destination """

    def __init__(self, dest_addr, run_at="now",
                 recurrence_time=None, recurrence_count=None):
        """ Making sure to pass on the scheduling variables to the 
        main task. Then adding mandatory variable dest_addr """

        super().__init__(run_at=run_at,
                         recurrence_time=recurrence_time,
                         recurrence_count=recurrence_count)
        self.dest_addr = dest_addr

    def run(self):
        print("Running ping to {}".format(self.dest_addr))
