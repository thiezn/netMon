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
        result = ': '.join([self.dest_addr, result[len(result)-1].decode('utf-8')])

        """
        # Parse the traceroute result
        for line in stdout.splitlines():
            line = line.decode('utf-8')
            ip_address = self.extract_ip_from_line(line)
            rtt = self.extract_rtt_from_line(line)
            if(ip_address and not line.startswith("traceroute to") and
               not line.startswith("Tracing")):
                trace_output.append({'hop': hop, 'ip_address': ip_address,
                                     'rtt': rtt})
                hop += 1
            elif '*' in line:
                trace_output.append({'hop': hop, 'ip_address': "*"})
                hop += 1
        """
        return result
