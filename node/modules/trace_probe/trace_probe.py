#!/usr/bin/env python

import socket


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
