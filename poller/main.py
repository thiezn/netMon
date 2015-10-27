#!/usr/bin/env python3

import logging
from poller import Poller
from probes.trace_probe import TraceProbe
from probes.ping_probe import PingProbe
from probes.http_probe import HttpProbe
from probe_storage import ProbeStorage
import time


def main():
    logging.basicConfig(filename='log.poller',
                        level=logging.DEBUG,
                        filemode='w',
                        format='%(asctime)s %(levelname)s %(message)s')

    logging.info('Loading poller...')
    poller = Poller('trucks')

    logging.info('Setting up probe storage db...')
    probe_storage = ProbeStorage()
    # probe_storage.clear_db()

    poller.start()

    try:
        """
        poller.add(PingProbe('149.210.184.36',
                             recurrence_time=1,
                             run_on_nodes=['trucks']))
        poller.add(TraceProbe('8.8.8.8', recurrence_time=3))
        poller.add(PingProbe('10.0.0.1', run_on_nodes=['miles']))
        """
        poller.add(HttpProbe('http://www.mortimer.nl/'))

        while True:
            # Here we can send probes to the poller
            # e.g. poller.add(IcmpProbe('127.0.0.1'))
            db_probes = probe_storage.get_probes()
            for probe in db_probes:
                if 'trucks' in probe['run_on_nodes']:
                    if probe['type'] == 'PingProbe':
                        poller.add(PingProbe(probe['dest_addr'],
                                             recurrence_time=probe['recurrence_time'],
                                             recurrence_count=probe['recurrence_count'],
                                             run_on_nodes=probe['run_on_nodes'],
                                             probe_id=probe['_id']))
                    if probe['type'] == 'TraceProbe':
                        poller.add(TraceProbe(probe['dest_addr'],
                                              recurrence_time=probe['recurrence_time'],
                                              recurrence_count=probe['recurrence_count'],
                                              run_on_nodes=probe['run_on_nodes']),
                                              probe_id=probe['_id'])
            time.sleep(5)
    except KeyboardInterrupt:
        poller.stop()
        print("\nThanks for joining!\n")

if __name__ == '__main__':
    main()
