#!/usr/bin/env python3

from app import app
from pymongo import MongoClient
from flask import render_template


class TaskStorage:

    def __init__(self, db_addr='127.0.0.1', db_port=27017):
        self.session = MongoClient(db_addr, db_port)
        self.db = self.session.task_database
        self.tasks = self.db.task_collection
        self.task_ids = []

    def get_tasks(self):
        """ Prints out all tasks """
        return self.tasks.find()


if __name__ == '__main__':
    task_storage = TaskStorage()
    task_storage.clear_db()
    task_storage.write({'test': 'test'})
    task_storage.get_tasks()


@app.route('/')
@app.route('/index')
def index():
    task_storage = TaskStorage()
    result = task_storage.get_tasks()

    tasks = []
    for task in result:
        tasks.append(task)

    return render_template("task_results.html", tasks=tasks)
