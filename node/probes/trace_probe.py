#!/usr/bin/env python3

# This probe runs the UNIX traceroute command and parses the output.
#
# Written by M. Mortimer
#
# v0.1 2-10-2015 - Initial version created based on trace script for infoblox

import subprocess       # For calling external shell commands
import re               # used for regular expression matching
from tasks import Task
import ipaddress


class TraceProbe(Task):

    def __init__(self, dest_addr, wait_time='1', max_hops='20',
                 icmp=True, *args, **kwargs):
        """ initialize  Task scheduling and traceroute options """
        super().__init__(**kwargs)
        self.dest_addr = dest_addr
        ipaddress.ip_address(dest_addr)  # check if valid ip
        self.wait_time = wait_time
        self.max_hops = max_hops
        self.icmp = icmp

    def run(self):
        """ Runs the traceroute, gets called by the task_manager """
        return self.traceroute()

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

    def db_record(self):
        """ Should return what we want to write to the
        database """
        return {'task_id': self.task_id,
                'type': self.name,
                'recurrence_time': self.recurrence_time,
                'recurrence_count': self.recurrence_count,
                'run_at': self.run_at,
                'dest_addr': self.dest_addr,
                'wait_time': self.wait_time,
                'max_hops': self.max_hops}

    def traceroute(self):
        """ This command runs a traceroute and returns
        the results """

        if self.icmp:
            # Use TCP traceroute to be able to traverse firewall
            parameters = ["sudo", "traceroute", "-I", "-n",
                          "-w " + self.wait_time, "-m " + self.max_hops,
                          "-n", "-q 1", self.dest_addr]
        else:
            # normal udp based traceroute
            parameters = ["traceroute", "-n", "-w " + self.wait_time,
                          "-m " + self.max_hops, "-n", "-q 1",
                          self.dest_addr]

        trace = subprocess.Popen(parameters,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
        stdout, stderr = trace.communicate()

        # Parse the traceroute result
        self.result = {'timestamp': self.run_at,
                       'hops': []}

        if stderr:
            self.result['error'] = stderr
            return True

        lines = stdout.splitlines()
        # remove first line "traceroute to..."
        del lines[0]

        for line in lines:
            line = line.decode('utf-8')
            ip_address = self.extract_ip_from_line(line)
            rtt = self.extract_rtt_from_line(line)
            if(ip_address):
                self.result['hops'].append({'ip_address': ip_address,
                                            'rtt': rtt})
            elif '*' in line:
                self.result['hops'].append({'ip_address': '*'})

        return True
