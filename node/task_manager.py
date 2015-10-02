#!/usr/bin/python3

from threading import Thread
from tcp_client import MessageHandler
import queue
from tasks import RegisterNode, UnregisterNode
import time


class TaskManager:

    def __init__(self):
        """ Initialising the task_queue and task_result_queue """
        self._task_queue = queue.Queue()
        self._task_result_queue = queue.Queue()
        self.message_handler = MessageHandler('127.0.0.1', 10666)

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

        self._manager_thread = Thread(target=self._task_manager,
                                      args=(self._task_queue,
                                            self.message_handler))
        self._manager_thread.daemon = True
        self._manager_thread.start()

    def stop(self):
        """ Gracefully stops the task manager """

        # unregister us from the message_handler
        self.add(UnregisterNode())
        # wait for all the pending tasks to finish
        # self._manager_thread.join()

    def get(self):
        """ returns a task from the task_result queue
        returns None if no result is available """
        pass

    def add(self, task):
        """ Adds a new task to the queue """
        self._task_queue.put(task)

    def _task_manager(self, task_queue, message_handler):

        if not self.message_handler.is_connected:
            # Register to the controller
            self.add(RegisterNode())
        while True:

            # First lets handle all the queued tasks
            if not self._task_queue.empty():
                current_task = self._task_queue.get()

                # Check if the task should be run already
                # If not, add it to the back of the queue
                if current_task.run_at <= time.time():

                    if(current_task.name == 'RegisterNode' and
                       not self.message_handler.is_connected):
                        current_task.run(self.message_handler)

                    elif(current_task.name == 'UnregisterNode' and
                         self.message_handler.is_connected):
                        current_task.run(self.message_handler)
                    elif 'IcmpProbe' in current_task.name:
                        current_task.run(self.message_handler)
                    else:
                        current_task.run()

                    if current_task.reschedule():
                        self._task_queue.put(current_task)
                else:
                    self._task_queue.put(current_task)

            # Now lets see if there are any messages received
            # from the controller.
            # TODO: I guess a lot of this logic should go into the message_handler
            # class instead of accessing the protocol directly
            self.message_handler.protocol.recv_message()
            if not self.message_handler.protocol.recv_queue.empty():
                print(self.message_handler.protocol.recv_queue.get())
