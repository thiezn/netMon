#!/usr/bin/env python3

import logging
from task_manager import TaskManager
# from config_manager import Configuration
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
        task_manager.add(PingProbe('149.210.184.36', recurrence_time=1))
        task_manager.add(TraceProbe('8.8.8.8', recurrence_time=3))
        task_manager.add(PingProbe('10.0.0.1'))
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
