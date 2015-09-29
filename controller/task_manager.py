#!/usr/bin/python3

from threading import Thread
import queue


class Task:
    """ Class describing a Task for use in the TaskManager """
    def run(self):
        """ Runs the specified task
        each task type has to overload this function """
        raise NotImplementedError


class TaskManager:

    def __init__(self, controller):
        # Create a task queue and start the manager in a seperate thread
        self._task_queue = queue.Queue()
        self._manager_thread = Thread(target=self._task_manager,
                                      args=(self._task_queue, ))
        self._manager_thread.daemon = True
        self._manager_thread.start()
        self.controller = controller

    def __repr__(self):
        """ Print the current queue contents """
        if not self._task_queue.empty():
            return "There's stuff in the task queue"
        else:
            return "The task queue is empty"

    def add(self, task):
        """ Adds a new task to the queue """
        self._task_queue.put(task)

    def run_now(self, task):
        """ Adds a new tasks to the front of the queue """

        print("run_now function not prioritised yet, "
              "have to implement dequeue?")
        self._task_queue.put(task)

    def _task_manager(self, task_queue):
        while True:
            while not self._task_queue.empty():
                current_task = self._task_queue.get()

                if current_task.name == 'register':
                    current_task.run()
