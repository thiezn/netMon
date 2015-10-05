#!/usr/bin/env python3

from pymongo import MongoClient


class ProbeStorage:

    def __init__(self, db_addr='127.0.0.1', db_port=27017):
        self.session = MongoClient(db_addr, db_port)
        self.db = self.session.probe_database
        self.probes = self.db.probe_collection
        self.probe_ids = []

    def clear_db(self): 
        """ Removes the full database """
        self.session.drop_database('probe_database')

    def write(self, probe):
        """ Writes the probe to the collection """
        client = MongoClient('127.0.0.1', 27017)

        self.probe_ids.append(self.probes.insert_one(probe).inserted_id)

    def get_probes(self):
        """ Prints out all probes """
        for item in self.probes.find():
            print(item)


if __name__ == '__main__':
    probe_storage = ProbeStorage()
    probe_storage.clear_db()
    probe_storage.write({'test': 'test'})
    probe_storage.get_probes()
