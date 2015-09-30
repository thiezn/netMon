#!/usr/bin/env python3

# Configuration Manager Module

import json


class Configuration:
    """ Configuration details for nodes and controllers """

    _BASE_DIR = "cfg/"
    _TCP_SERVER_FILE = _BASE_DIR + "tcp_server.cfg"

    def __init__(self):
        """ Open configuration files """

        with open(self._TCP_SERVER_FILE) as tcp_server_file:
            self.tcp_server = json.load(tcp_server_file)[0]

        if('server' not in self.tcp_server and
           'port' not in self.tcp_server):
            print("server/port not found in {}".format(self._TCP_SERVER_FILE))
        else:
            print("tcp_server {}:{} loaded from configuration"
                  .format(self.tcp_server['address'], self.tcp_server['port']))


def main():
    pass

if __name__ == '__main__':
    main()
