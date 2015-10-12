#!/usr/bin/env python3

import logging
from task_manager import TaskManager
from probes.trace_probe import TraceProbe
from probes.ping_probe import PingProbe
from task_storage import TaskStorage
import time
from config_manager import Configuration


def main():
    logging.basicConfig(filename='log.main',
                        level=logging.DEBUG,
                        filemode='w',
                        format='%(asctime)s %(levelname)s %(message)s')

    logging.info('Loading local configration...')
    config = Configuration()
    node_details = config.load_node_main()

    logging.info('Loading task_manager...')
    task_manager = TaskManager(node_details)

    logging.info('Setting up task storage db...')
    task_storage = TaskStorage()

    task_manager.start()

    try:
        task_manager.add(PingProbe('149.210.184.36',
                                   recurrence_time=1,
                                   run_on_nodes=['trucks']))
        task_manager.add(TraceProbe('8.8.8.8',
                                    recurrence_time=3))
        task_manager.add(PingProbe('10.0.0.1',
                                   run_on_nodes=['miles']))

        task_list = []  # Store tuple dest_addr/run_at to uniquefy tasks
        while True:
            # Here we can send probes to the task_manager
            # e.g. task_manager.add(IcmpProbe('127.0.0.1'))
            db_tasks = task_storage.get_tasks()
            for task in db_tasks:
                if(node_details['name'] in task['run_on_nodes'] and
                   task['dest_addr'] not in task_list):
                    task_list.append(task['dest_addr'])
                    if task['type'] == 'PingProbe':
                        task_manager.add(PingProbe(task['dest_addr'],
                                         recurrence_time=task['recurrence_time'],
                                         recurrence_count=task['recurrence_count'],
                                         run_on_nodes=task['run_on_nodes']))
                    if task['type'] == 'TraceProbe':
                        task_list.append(task['_id'])
                        task_manager.add(TraceProbe(task['dest_addr'],
                                         recurrence_time=task['recurrence_time'],
                                         recurrence_count=task['recurrence_count'],
                                         run_on_nodes=task['run_on_nodes']))
            time.sleep(5)
    except KeyboardInterrupt:
        task_manager.stop()
        print("\nThanks for joining!\n")
if __name__ == '__main__':
    main()
