#!/usr/bin/env python3

# This probe runs the UNIX traceroute command and parses the output.
#
# Written by M. Mortimer
#
# v0.1 2-10-2015 - Initial version created based on trace script for infoblox

import sys
import subprocess       # For calling external shell commands
import re               # used for regular expression matching
from tasks import Task


class TraceProbe(Task):

    def __init__(self, dest_ip, wait_time='1', max_hops='20', icmp=False,
                 run_at="now", recurrence_time=None, recurrence_count=None):
        """ initialize  Task scheduling and traceroute options """
        super().__init__(run_at=run_at,
                         recurrence_time=recurrence_time,
                         recurrence_count=recurrence_count)
        self.dest_ip = dest_ip
        self.wait_time = wait_time
        self.max_hops = max_hops
        self.icmp = icmp

    def run(self):
        """ Runs the traceroute, gets called by the task_manager """
        print(self.traceroute())

    def extract_rtt_from_line(self, line):
        """ Fetch the first occurance of the round-trip time of
        a traceroute output """

        if line:
            rtt = line.split(' ms')[0].split()[-1]
            return rtt
        else:
            return None

    def extract_ip_from_line(self, line):
        """ Check a string line to see if there's an valid IP address

        TODO: Check if we can replace this with the ipaddress module from
        python 3?
        """
        ip = re.compile('(([2][5][0-5]\.)|'
                        '([2][0-4][0-9]\.)|'
                        '([0-1]?[0-9]?[0-9]\.)){3}'
                        '(([2][5][0-5])|([2][0-4][0-9])|'
                        '([0-1]?[0-9]?[0-9]))')
        match = ip.search(line)

        if match:
            return match.group()
        else:
            return None

    def traceroute(self):
        """ This command runs a traceroute and returns
        the results """

        if sys.platform.startswith('linux'):
            if self.icmp:
                # Use TCP traceroute to be able to traverse firewall
                parameters = ["sudo", "traceroute", "-I", "-n",
                              "-w " + self.wait_time, "-m " + self.max_hops,
                              "-n", "-q 1", self.dest_ip]
            else:
                # normal udp based traceroute
                parameters = ["traceroute", "-n", "-w " + self.wait_time,
                              "-m " + self.max_hops, "-n", "-q 1",
                              self.dest_ip]
        else:
            # assume we're on windows.. Yes I know, maybe
            # someday we'll introduce MacOS support :)
            parameters = ["C:\Windows\System32\\tracert.exe", "-d",
                          "-w", self.wait_time, '-h', self.max_hops,
                          self.dest_ip]

        trace = subprocess.Popen(parameters,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
        stdout, stderr = trace.communicate()

        # Parse the traceroute result
        hop = 1
        trace_output = []
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

        return trace_output