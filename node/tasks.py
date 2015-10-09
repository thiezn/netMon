#!/usr/bin/env python3

import time
from datetime import datetime


class Task:
    """ Class describing a Task for use in the TaskManager

    Args:
        run_at: when should the task run, use "now" for a immediate task
        recurrence_time: after how many seconds should the task re-occur
        recurrence_count: how often should the task re-occur
    """

    def __init__(self, *args, **kwargs):
        """ Define the task name, set the run at time and define
         recurrence if any

        kwargs:
            run_at: when should the task run, use "now" for a immediate task
            recurrence_time: after how many seconds should the task reoccur
            recurrence_count: how often should the task reoccur
        """

        run_at = kwargs.get('run_at', "now")
        recurrence_time = kwargs.get('recurrence_time', None)
        recurrence_count = kwargs.get('recurrence_count', None)

        if recurrence_count and not recurrence_time:
            raise ValueError('Have to provide recurrence_time when '
                             'providing recurrence_count')

        if run_at == "now":
            self.run_at = time.time()
        else:
            self.run_at = run_at

        self.name = self.__class__.__name__
        self.recurrence_time = recurrence_time
        self.recurrence_count = recurrence_count
        self.task_id = None

    def db_record(self):
        """ Should return what we want to write to the
        database """
        return {'type': self.name,
                'recurrence_time': self.recurrence_time,
                'recurrence_count': self.recurrence_count,
                'run_at': datetime.fromtimestamp(int(self.run_at)).strftime('%Y-%m-%d %H:%M:%S')}

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
            # no persistent reoccuring task
            self.run_at += self.recurrence_time
            self.recurrence_count -= 1
            return True
        else:
            # one off task
            return False

    def run(self):
        """ Runs the specified task
        each task type has to overload this function """
        raise NotImplementedError


class RemoteTask(Task):
    """ Task that need to communicate through the message_handler """

    def __init__(self, message_handler, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.message_handler = message_handler


class RegisterNode(RemoteTask):
    """ Registers a node to the message_handler """

    def __init__(self, node_details, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.node_details = node_details

    def run(self):
        self.message_handler.register(self.node_details)


class UnregisterNode(RemoteTask):
    """ Unregisters a node from the message_handler """

    def __init__(self, node_details, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.node_details = node_details

    def run(self):
        self.message_handler.unregister(self.node_details)
