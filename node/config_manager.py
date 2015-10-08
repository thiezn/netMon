#!/usr/bin/env python3

# Configuration Manager Module

import json


class Configuration:
    """ Configuration details for nodes and controllers """

    _BASE_DIR = "cfg/"
    _TCP_SERVER_FILE = "tcp_server.cfg"
    _NODE_MAIN_FILE = "node_main.cfg"

    def _load_cfg_file(self, filename):
        """ Open configuration files """

        url = "%s%s" % (self._BASE_DIR, filename)
        with open(url) as cfg_file:
            result = json.load(cfg_file)[0]

        cfg_file.close()
        return result

    def load_tcp_server(self):
        config = self._load_cfg_file(self._TCP_SERVER_FILE)

        if('server' not in config and
           'port' not in config):
            print("server/port not found in {}".format(self._TCP_SERVER_FILE))
        else:
            print("tcp_server {}:{} loaded from configuration"
                  .format(config['address'], config['port']))
        return config


    def load_node_main(self):
        config = self._load_cfg_file(self._NODE_MAIN_FILE)
        return config


def main():
    config = Configuration()
    print(config.load_tcp_server())
    print(config.load_node_main())

if __name__ == '__main__':
    main()
