#!/usr/bin/env python3

from bson.objectid import ObjectId
from pymongo import MongoClient
import logging

logger = logging.getLogger(__name__)


class ProbeStorage:

    def __init__(self, db_addr='127.0.0.1', db_port=27017):
        self.session = MongoClient(db_addr, db_port)
        self.db = self.session.probe_database
        self.probes = self.db.probe_collection

    def clear_db(self):
        """ Removes the full database """
        self.session.drop_database('probe_database')

    def check_if_exists(self, probe):
        """ Check if the probe already exists in db """

        return self.probes.find_one({'dest_addr': probe.dest_addr},
                                    {'run_at': probe.run_at})

    def add(self, probe):
        """ Adds a probe Probe to the database

        Args:
            probe: A probe Probe object
        return:
            probe_id: _id value of mongodb document
        """
        logger.info('adding probe to the queue: {}'.format(probe))
        return self.probes.insert_one(probe.db_record()).inserted_id

    def update(self, probe, upsert=False):
        """ Updates a probe Probe with the latest result

        Args:
            probe: Probe Probe including it's results
            upsert: If the probe is not yet present in the db it will
                    add if if this is set to True
        """
        logger.info('updating probe_id {} with result {}'
                    .format(probe.probe_id, probe))
        self.probes.update_one({'_id': probe.probe_id},
                               {'$addToSet': {'result': probe.result}},
                               upsert=upsert)

    def get_probes(self):
        """ retrieve all probes """
        return self.probes.find()

    def get_probe(self, probe_id):
        """ Returns a single probe """
        print(self.probes.find_one({"_id": ObjectId(probe_id)}))


if __name__ == '__main__':
    probe_storage = ProbeStorage()
    for probe in probe_storage.get_probes():
        print("%s\n" % probe['type'])
