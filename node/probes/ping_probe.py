#!/usr/bin/env python3

from tasks import Task
import subprocess
import sys


class PingProbe(Task):
    """ Runs an ICMP probe to the provided destination """

    def __init__(self, dest_addr, count='10', preload='10', timeout='1',
                 run_at="now", recurrence_time=None, recurrence_count=None):
        """ Making sure to pass on the scheduling variables to the
        main task.

        Args:
            count: amount of icmp probes to send
            preload: amount of probes to send simultaneously
            timeout: amount of seconds before a probe times out
        """

        super().__init__(run_at=run_at,
                         recurrence_time=recurrence_time,
                         recurrence_count=recurrence_count)
        self.dest_addr = dest_addr
        self.count = count
        self.preload = preload
        self.timeout = timeout

    def run(self):
        return self.ping()

    def ping(self):
        """ Runs a ping using the OS ping function """

        if sys.platform.startswith('linux'):
            parameters = ["ping", self.dest_addr,
                          "-c " + self.count,
                          "-l " + self.preload,
                          "-W " + self.timeout]
        else:
            # In the future perhaps build in support for windows and macos
            # ping support. For now just return None
            return None

        trace = subprocess.Popen(parameters,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
        stdout, stderr = trace.communicate()

        result = stdout.splitlines()
        result = result[len(result)-1].decode('utf-8')
        result = result.split()[3].split('/')
        result = {'type': self.name,
                  'run_at': self.run_at,
                  'dest_addr': self.dest_addr,
                  'min': result[0],
                  'avg': result[1],
                  'max': result[2],
                  'mdev': result[3]}

        return result
