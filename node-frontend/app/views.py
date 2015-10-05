#!/usr/bin/env python3

from app import app
from pymongo import MongoClient
from flask import render_template
from datetime import datetime


class ProbeStorage:

    def __init__(self, db_addr='127.0.0.1', db_port=27017):
        self.session = MongoClient(db_addr, db_port)
        self.db = self.session.probe_database
        self.probes = self.db.probe_collection
        self.probe_ids = []

    def get_probes(self):
        """ Prints out all probes """
        return self.probes.find()


if __name__ == '__main__':
    probe_storage = ProbeStorage()
    probe_storage.clear_db()
    probe_storage.write({'test': 'test'})
    probe_storage.get_probes()


@app.route('/')
@app.route('/index')
def index():
    probe_storage = ProbeStorage()
    result = probe_storage.get_probes()

    probes = []
    for probe in result:
        probe['run_at'] = datetime.fromtimestamp(int(probe['run_at']))
        probes.append(probe)

    return render_template("probe_results.html", probes=probes)
