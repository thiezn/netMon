#!/usr/bin/env python3

import logging
from task_manager import TaskManager
from config_manager import Configuration


def main():
    #    config = Configuration()
    logging.basicConfig(filename='log.main',
                        level=logging.DEBUG,
                        filemode='w',
                        format='%(asctime)s %(levelname)s %(message)s')

    logging.info('Launching the node controller tcp server...(NOT REALLY)')

    logging.info('Loading task_manager...')
    task_manager = TaskManager()

    task_manager.run()

    try:
        while True:
            # Here we can send probes to the task_manager
            # e.g. task_manager.add(IcmpProbe('127.0.0.1'))
            pass
    except KeyboardInterrupt:
        print("\nThanks for Joining!\n")

if __name__ == '__main__':
    main()
