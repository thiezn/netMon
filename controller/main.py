#!/usr/bin/env python3

import logging
from task_manager import TaskManager
from config_manager import Configuration
import time
from probes.icmp_probe import IcmpProbe


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
        while True:
            # Here we can send probes to the task_manager
            # e.g. task_manager.add(IcmpProbe('127.0.0.1'))
            task_manager.add(IcmpProbe('10.0.0.1'))
            task_manager.add(IcmpProbe('127.0.0.1', run_at=time.time()+10))
            time.sleep(2)
    except KeyboardInterrupt:
        task_manager.stop()
        print("\nThanks for Joining!\n")
        time.sleep(1)    # Give it some time to deliver the unregister message

if __name__ == '__main__':
    main()
