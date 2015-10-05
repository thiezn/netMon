#!/usr/bin/env python3

from tasks import Task
import subprocess
import sys


class PingProbe(Task):
    """ Runs an ICMP probe to the provided destination """

    def __init__(self, task_storage, dest_addr, count='10', preload='10',
                 timeout='1', run_at="now", recurrence_time=None,
                 recurrence_count=None):
        """ Making sure to pass on the scheduling variables to the
        main task.

        Args:
            count: amount of icmp probes to send
            preload: amount of probes to send simultaneously
            timeout: amount of seconds before a probe times out
        """

        super().__init__(task_storage,
                         run_at=run_at,
                         recurrence_time=recurrence_time,
                         recurrence_count=recurrence_count,
                         is_remote=False)
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
            return False

        trace = subprocess.Popen(parameters,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
        stdout, stderr = trace.communicate()

        if stderr:
            self.result = {'timestamp': self.run_at,
                           'error': stderr.decode('utf-8').strip()}
            return False

        result = stdout.splitlines()
        second_last_line = result[len(result)-2].decode('utf-8').split()
        last_line = result[len(result)-1].decode('utf-8')
        if not last_line:
            # if the last line is empty
            # none of the packets arrived
            self.result = {'timestamp': self.run_at,
                           'error': 'Host unreachable',
                           'packets_sent': second_last_line[0],
                           'packets_recv': second_last_line[3]}
        else:
            last_line = last_line.split()[3].split('/')
            self.result = {'timestamp': self.run_at,
                           'min': last_line[0],
                           'avg': last_line[1],
                           'max': last_line[2],
                           'mdev': last_line[3],
                           'packets_sent': second_last_line[0],
                           'packets_recv': second_last_line[3]}

        return True
