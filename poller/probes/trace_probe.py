#!/usr/bin/env python3

# This probe runs the UNIX traceroute command and parses the output.
#
# Written by M. Mortimer
#
# v0.1 2-10-2015 - Initial version created based on trace script for infoblox

import subprocess       # For calling external shell commands
from .probes import Probe
import ipaddress


class TraceProbe(Probe):

    def __init__(self, dest_addr, wait_time='1', max_hops='20',
                 icmp=True, *args, **kwargs):
        """ initialize  Probe scheduling and traceroute options """
        super().__init__(**kwargs)
        self.dest_addr = dest_addr
        ipaddress.ip_address(dest_addr)  # check if valid ip
        self.wait_time = wait_time
        self.max_hops = max_hops
        self.icmp = icmp

    def run(self):
        """ Runs the traceroute, gets called by the probe_manager """
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
        """ Check a string line to see if there's an valid IP address """

        ip = line.split()[1]
        try:
            ipaddress.ip_address(ip)
        except ValueError:
            if ip != "*":
                return None
        return ip

    def db_record(self):
        """ Should return what we want to write to the
        database """
        return {"probe_id": self.probe_id,
                "type": self.name,
                "recurrence_time": self.recurrence_time,
                "recurrence_count": self.recurrence_count,
                "run_at": self.run_at,
                "run_on_nodes": self.run_on_nodes,
                "run_on_groups": self.run_on_groups,
                "dest_addr": self.dest_addr,
                "wait_time": self.wait_time,
                "max_hops": self.max_hops}

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


if __name__ == '__main__':
    probe = TraceProbe('8.8.8.8')
    print(probe)
