#!/usr/bin/env python3

import logging
from task_manager import TaskManager
# from config_manager import Configuration
import time
from probes.icmp_probe import IcmpProbe
from probes.trace_probe import TraceProbe
from probes.ping_probe import PingProbe
from task_storage import TaskStorage


def main():
    #    config = Configuration()
    logging.basicConfig(filename='log.main',
                        level=logging.DEBUG,
                        filemode='w',
                        format='%(asctime)s %(levelname)s %(message)s')

    logging.info('Loading task_manager...')
    task_manager = TaskManager()

    logging.info('Setting up task storage db...')
    task_storage = TaskStorage()

    task_manager.start()

    try:
        #task_manager.add(IcmpProbe(task_storage, 'one time scheduled ping after 10sec',
         #                          run_at=time.time()+10))
        #task_manager.add(IcmpProbe(task_storage, '10x recurring task each second',
         #                          recurrence_time=1, recurrence_count=10))
        task_manager.add(PingProbe(task_storage, '149.210.184.36',
                                   recurrence_time=15))
        task_manager.add(TraceProbe(task_storage, '8.8.8.8'))
        task_manager.add(PingProbe(task_storage, 'bla'))
        task_manager.add(PingProbe(task_storage, '10.0.0.1',
                                   recurrence_time=1, recurrence_count=5))
        while True:
            # Here we can send probes to the task_manager
            # e.g. task_manager.add(IcmpProbe('127.0.0.1'))
            pass
    except KeyboardInterrupt:
        task_manager.stop()
        print("\nThanks for joining!\n")
        print("here are all current tasks in db")
        task_storage.get_tasks()
if __name__ == '__main__':
    main()
