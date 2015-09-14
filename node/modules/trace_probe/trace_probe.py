#!/usr/bin/env python

import socket
import sys
import subprocess
import re


def extract_ip_from_line(line):
    """ Check a string line to see if there's an valid IP address """
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


def extract_rtt_from_line(line):
    """ Fetch the first occurance of the round-trip time of
    a traceroute output """

    if line:
        rtt = line.split(' ms')[0].split()[-1]
        return rtt
    else:
        return None


def traceroute(dest_ip, wait_time=1, max_hops=20, icmp=False):
    """ This command runs a traceroute on the CLI and returns
    the results """

    if sys.platform == 'linux2':
        if icmp:
            # Use TCP traceroute to be able to traverse firewall
            parameters = ["sudo", "traceroute", "-I", "-n",
                          "-w", str(wait_time), "-m", str(max_hops),
                          "-n", "-q 1", dest_ip]
        else:
            # normal udp based traceroute
            parameters = ["traceroute", "-n", "-w", str(wait_time),
                          "-m", str(max_hops), "-n", "-q 1", dest_ip]
    else:
        # assume we're on windows.. Yes I know, maybe
        # someday we'll introduce MacOS support :)
        parameters = ["C:\Windows\System32\\tracert.exe", "-d",
                      "-w", wait_time, '-h', max_hops, dest_ip]

    trace = subprocess.Popen(parameters,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
    stdout, stderr = trace.communicate()

    # Parse the traceroute result
    hop = 1
    trace_output = []
    for line in stdout.splitlines():
        ip_address = extract_ip_from_line(line)
        rtt = extract_rtt_from_line(line)
        if(ip_address and not line.startswith("traceroute to") and
           not line.startswith("Tracing")):
            trace_output.append({'hop': hop, 'ip_address': ip_address,
                                 'rtt': rtt})
            hop += 1
        elif '*' in line:
            trace_output.append({'hop': hop, 'ip_address': "*"})
            hop += 1

    return trace_output


class TraceProbe:
    """ Trace probe (a.k.a traceroute) """

    def __init__(self, dest='127.0.0.1',
                 maxhops=10, timeout=1,
                 src_port=33434):
        """ Initialise the traceroute options """

        self.dest = dest
        self.maxhops = maxhops
        self.timeout = timeout
        self.src_port = src_port

    def __repr__(self):
        """ print out the job type when printing the object """
        return "Traceroute to %s" % self.dest

    def run(self):
        """ Starts the Trace

        Returns a list of dictionary containing hop and latency """

        result = []
        icmp = socket.getprotobyname('icmp')
        udp = socket.getprotobyname('udp')
        ttl = 1

        while True:
            recv_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
            send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, udp)
            send_socket.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
            recv_socket.bind(("", self.src_port))
            send_socket.sendto("", (self.dest, self.src_port))

            curr_addr = None
            try:
                _, curr_addr = recv_socket.recvfrom(512)
                curr_addr = curr_addr[0]
            except socket.error:
                pass
            finally:
                send_socket.close()
                recv_socket.close()

            result.append({'hop': ttl, 'ip': curr_addr})

            ttl += 1
            if curr_addr == self.dest or ttl > self.maxhops:
                break

        return result

if __name__ == '__main__':
    trace_result = traceroute('8.8.8.8')
    for hop in trace_result:
        print hop
