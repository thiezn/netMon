#!/usr/bin/env python3

import logging
from poller import Poller
from probes.trace_probe import TraceProbe
from probes.ping_probe import PingProbe
from probe_storage import ProbeStorage
import time


def main():
    logging.basicConfig(filename='log.poller',
                        level=logging.DEBUG,
                        filemode='w',
                        format='%(asctime)s %(levelname)s %(message)s')

    logging.info('Loading poller...')
    poller = Poller('trucks')

    logging.info('Setting up task storage db...')
    probe_storage = ProbeStorage()

    poller.start()

    try:
        poller.add(PingProbe('149.210.184.36',
                             recurrence_time=1,
                             run_on_nodes=['trucks']))
        poller.add(TraceProbe('8.8.8.8', recurrence_time=3))
        poller.add(PingProbe('10.0.0.1', run_on_nodes=['miles']))

        while True:
            # Here we can send probes to the poller
            # e.g. poller.add(IcmpProbe('127.0.0.1'))
            db_probes = probe_storage.get_probes()
            for task in db_probes:
                if 'trucks' in task['run_on_nodes']:
                    if task['type'] == 'PingProbe':
                        poller.add(PingProbe(task['dest_addr'],
                                             recurrence_time=task['recurrence_time'],
                                             recurrence_count=task['recurrence_count'],
                                             run_on_nodes=task['run_on_nodes']))
                    if task['type'] == 'TraceProbe':
                        poller.add(TraceProbe(task['dest_addr'],
                                              recurrence_time=task['recurrence_time'],
                                              recurrence_count=task['recurrence_count'],
                                              run_on_nodes=task['run_on_nodes']))
            time.sleep(5)
    except KeyboardInterrupt:
        poller.stop()
        print("\nThanks for joining!\n")
if __name__ == '__main__':
    main()
