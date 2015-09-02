#!/usr/bin/env python


class IcmpProbe:
    """ ICMP probe (a.k.a ping) """

    def __init__(self, dest='127.0.0.1'):
        self.dest = dest
        self.state = 'stopped'
        self._min = 0
        self._max = 0
        self._avg = 0

    @property
    def result(self):
        """ returns the last known min/max/avg response in ms """
        current_time = '13:50'
        return {'current_time': current_time,
                'min': self._min,
                'max': self._max,
                'avg': self._avg}

    def run(self):
        """ Starts the ICMP poll
        TODO - Need to utilise threading so we can start/stop/pause
        this """
        self.state = 'running'
        print("Ping %s" % self.dest)

    def pause(self):
        self.state = 'paused'

    def stop(self):
        self.state = 'stopped'
