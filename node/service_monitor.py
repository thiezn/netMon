#!/usr/bin/env python3

# Service Monitor
#
# Module to monitor all application components. This
# relies heavily on the psutil package which gives a cross
# platform interface to various OS resources

import psutil


class ServiceMonitor():
    """ Monitoring the various application daemons and
    OS statistics """

    def net_connections(self):
        """ Returns the current network connections """
        return psutil.net_connections()

    def users(self):
        """ Return current logged on users """
        return psutil.users()


def main():
    service_monitor = ServiceMonitor()
    print("Current network conn {}".format(service_monitor.net_connections()))
    print("Current logged on users {}".format(service_monitor.users()))

if __name__ == '__main__':
    main()
