#!/usr/bin/python3

from config_manager import Configuration
from threading import Thread
from tcp_client import MessageHandler
import queue
from tasks import RegisterNode, UnregisterNode
import time
import logging
from task_storage import TaskStorage

logger = logging.getLogger(__name__)


class TaskManager:

    def __init__(self):
        """ Initialising the task_queue and task_result_queue """
        config = Configuration()
        self.node_details = config.load_node_main()

        self._task_queue = queue.Queue()
        self._task_result_queue = queue.Queue()
        self.message_handler = MessageHandler('127.0.0.1', 10666)
        self.task_storage = TaskStorage()
        self.task_storage.clear_db()

    def __repr__(self):
        """ Print the current queue contents """
        if not self._task_queue.empty():
            return "There's stuff in the task queue"
        else:
            return "The task queue is empty"

    def start(self):
        """ Start the task manager

        Here we will start the messsage_handler and
        run the main task loop in a seperate thread """

        logger.info('Starting task manager thread')
        self._manager_thread = Thread(target=self._task_manager,
                                      args=(self.message_handler,))
        self._manager_thread.daemon = True
        self._manager_thread.start()

        self._task_result_thread = Thread(target=self._task_result_handler)
        self._task_result_thread.daemon = True
        self._task_result_thread.start()

    def stop(self):
        """ Gracefully stops the task manager """

        logger.info('Stopping task manager...')
        # unregister us from the message_handler
        self.add(UnregisterNode(self.node_details, self.message_handler))

    def add(self, task):
        """ Adds a new task to the queue """
        logger.debug('Task {} added to the task_manager queue'
                     .format(task.name))
        task.task_id = self.task_storage.add(task)
        self._task_queue.put(task)

    def _task_result_handler(self):
        """ Handles received task results """
        while True:
            while not self._task_result_queue.empty():
                task = self._task_result_queue.get()
                print("Updating task ID {}".format(task.task_id))
                self.task_storage.update(task)

    def _task_manager(self, message_handler):

        if not self.message_handler.is_connected:
            # Register to the controller
            # note we don not register this task to the task_manager
            # as we don't want to process messages until the
            # connection is established
            RegisterNode(self.node_details, self.message_handler).run()

        while True:
            # First lets handle all the queued tasks
            if not self._task_queue.empty():
                current_task = self._task_queue.get()

                # Check if the task should be run already
                # If not, add it to the back of the queue
                if current_task.run_at <= time.time():

                    if(current_task.name == 'UnregisterNode'):
                        # Quit the task_manager when this is handled
                        current_task.run()
                        logging.info('Task manager stopped')
                        break

                    result = current_task.run()
                    if result:
                        self._task_result_queue.put(current_task)

                    if current_task.reschedule():
                        # reschedule the task if needed
                        self._task_queue.put(current_task)
                else:
                    self._task_queue.put(current_task)

            # Now lets see if there are any messages received
            # from the controller.
            # Nothing happens here yet but we could for instance
            # accept new scheduled tasks from the frontend/controller
            # TODO: I guess a lot of this logic should go into the
            # message_handler class instead of accessing the protocol
            # directly
            self.message_handler.protocol.recv_message()
            if not self.message_handler.protocol.recv_queue.empty():
                print(self.message_handler.protocol.recv_queue.get())
