#!/usr/bin/env python

from jobs import Job


class IcmpProbe(Job):
    """ ICMP probe (a.k.a ping) """

    def __init__(self, dest='127.0.0.1', count=10):
        self.dest = dest
        self.count = count
        self._min = 0
        self._max = 0
        self._avg = 0

    def __repr__(self):
        """ print out the job type when printing the object """
        return "ICMP to %s" % self.dest

    def run(self):
        """ Starts the ICMP poll
        returns the last known min/max/avg response in ms """
        current_time = '13:50'
        for _ in range(self.count-1):
            self._avg += 1

        return {'current_time': current_time,
                'min': self._min,
                'max': self._max,
                'avg': self._avg}
