#!/usr/bin/env python3

import logging
from task_manager import TaskManager
# from config_manager import Configuration
import time
from probes.icmp_probe import IcmpProbe
from probes.trace_probe import TraceProbe
from probes.ping_probe import PingProbe


def main():
    #    config = Configuration()
    logging.basicConfig(filename='log.main',
                        level=logging.DEBUG,
                        filemode='w',
                        format='%(asctime)s %(levelname)s %(message)s')

    logging.info('Launching the node controller tcp server...(NOT REALLY)')

    logging.info('Loading task_manager...')
    task_manager = TaskManager()

    task_manager.start()

    try:
        task_manager.add(IcmpProbe('one time scheduled ping after 10sec',
                                   run_at=time.time()+10))
        task_manager.add(IcmpProbe('10x recurring task each second',
                                   recurrence_time=1, recurrence_count=10))
        task_manager.add(PingProbe('149.210.184.36', recurrence_time=15))
        task_manager.add(TraceProbe('8.8.8.8'))
        while True:
            # Here we can send probes to the task_manager
            # e.g. task_manager.add(IcmpProbe('127.0.0.1'))
            pass
    except KeyboardInterrupt:
        task_manager.stop()
        print("\nThanks for joining!\n")
        time.sleep(2)

if __name__ == '__main__':
    main()
