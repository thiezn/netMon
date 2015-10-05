#!/usr/bin/env python3

from pymongo import MongoClient
import logging

logger = logging.getLogger(__name__)


class TaskStorage:

    def __init__(self, db_addr='127.0.0.1', db_port=27017):
        self.session = MongoClient(db_addr, db_port)
        self.db = self.session.task_database
        self.tasks = self.db.task_collection

    def clear_db(self):
        """ Removes the full database """
        self.session.drop_database('task_database')

    def add(self, task):
        """ Adds a task Task to the database

        Args:
            task: A task Task object
        return:
            task_id: _id value of mongodb document
        """
        logger.info('adding task to the queue: {}'.format(task))
        return self.tasks.insert_one(task).inserted_id

    def update(self, task, upsert=False):
        """ Updates a task Task with the latest result

        Args:
            task: Task Task including it's results
            upsert: If the task is not yet present in the db it will
                    add if if this is set to True
        """
        logger.info('updating task_id {} with result {}'
                    .format(task.task_id, task))
        self.tasks.update_one({'_id': task.task_id},
                              {'$addToSet': {'result': task.result}},
                              upsert=upsert)

    def get_tasks(self):
        """ Prints out all tasks """
        for item in self.tasks.find():
            print(item)


if __name__ == '__main__':
    task_storage = TaskStorage()
    task_storage.clear_db()
    task_storage.add({'test': 'test'})
    task_storage.get_tasks()
