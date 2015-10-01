#!/usr/bin/env python3

import time


class Task:
    """ Class describing a Task for use in the TaskManager

    Args:
        run_at: when should the task run, use "now" for a immediate task
        recurrence_time: after how many seconds should the task re-occur
        recurrence_count: how often should the task re-occur
    """

    def __init__(self, run_at="now",
                 recurrence_time=None, recurrence_count=None):
        """ Define the task name, set the run at time and define
         recurrence if any

        Args:
            run_at: when should the task run, use "now" for a immediate task
            recurrence_time: after how many seconds should the task reoccur
            recurrence_count: how often should the task reoccur
        """

        self.name = self.__class__.__name__
        self.recurrence_time = recurrence_time
        self.recurrence_count = recurrence_count

        if recurrence_count and not recurrence_time:
            raise ValueError('Have to provide recurrence_time when '
                             'providing recurrence_count')

        if run_at == "now":
            self.run_at = time.time()
        else:
            self.run_at = run_at

    def run(self):
        """ Runs the specified task
        each task type has to overload this function """
        raise NotImplementedError


class RegisterNode(Task):
    """ Registers a node to the message_handler """

    def run(self, message_handler):
        message_handler.register()


class UnregisterNode(Task):
    """ Unregisters a node from the message_handler """

    def run(self, message_handler):
        message_handler.unregister()
