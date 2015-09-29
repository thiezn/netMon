#!/usr/bin/env python3

import logging
from task_manager import TaskManager
from tcp_client import MessageHandler
from tasks import RegisterNode


def main():
    logging.basicConfig(filename='log.main',
                        level=logging.DEBUG,
                        filemode='w',
                        format='%(asctime)s %(levelname)s %(message)s')

    logging.info('Launching the node controller tcp server...(NOT REALLY)')

    logging.info('Setting up TCP connection to node controller server')
    message_handler = MessageHandler('127.0.0.1', 10666)
    logging.info('Registering to node controller server')
    message_handler.register()

    logging.info('Loading task_manager...')
    task_manager = TaskManager(message_handler)

    try:
        while True:
            if not message_handler.is_connected:
                # (re)establish connection to node controller
                task_manager.run_now(RegisterNode())
    except KeyboardInterrupt:
        print("\nThanks for Joining!\n")

if __name__ == '__main__':
    main()
