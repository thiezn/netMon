#!/usr/bin/env python

class Task:
    """ Class describing a Task for use in the TaskManager """

    def __init__(self, name):
        """ Each Task should have a descriptive name
        examples are register, icmp_probe """
        self.name = name

    def run(self):
        """ Runs the specified task
        each task type has to overload this function """
        raise NotImplementedError


class RegisterNode(Task):
    """ Registers a node to the message_handler """

    def __init__(self):
        self.name = "register"

    def run(self, message_handler):
        message_handler.register()

class UnregisterNode(Task):
    """ Unregisters a node from the message_handler """

    def __init__(self):
        self.name = "unregister"

    def run(self, message_handler):
        message_handler.unregister()
