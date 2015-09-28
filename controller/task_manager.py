#!/usr/bin/env python3

# Task Manager
#
# Responsible for handling tasks within the application
# Built upon a asyncio event loop able to run tasks
# asyncronously
#
# Various system components interface with this
# module to run tasks and retrieve task results from
# other components

# Check Example 1 from PEP-0492, perhaps a class like that can
# be used to put tasks on a queue and iterate through them
# https://www.python.org/dev/peps/pep-0492/#id58

# Since we would like to be able to start stop and cancel
# tasks have a look at the loop.call_soon, call_later, call_at
# functions

import asyncio


async def run_task(task_id):
    """ Coroutine running a tasks in the asyncio loop """
    await asyncio.sleep(1)
    print("Task {} completed".format(task_id))

async def task_manager():
    await asyncio.wait([run_task(1), run_task(2)])

if __name__ == '__main__':
    """ the main loop starts here """

    loop = asyncio.get_event_loop()
    loop.run_until_complete(task_manager())
    loop.close()
