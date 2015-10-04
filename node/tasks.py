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
                 recurrence_time=None, recurrence_count=0):
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

    def reschedule(self):
        """ Check if the Task has to reoccur again

        This should be run by the task_manager class each time
        it has run a Task that has the potential to be run again
        """

        if self.recurrence_time and not self.recurrence_count:
            # persistent reoccuring task
            self.run_at += self.recurrence_time
            return True
        elif self.recurrence_time and self.recurrence_count > 1:
            self.run_at += self.recurrence_time
            self.recurrence_count -= 1
            return True
        else:
            return False

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
