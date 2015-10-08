#!/usr/bin/env python3

from bson.objectid import ObjectId
from pymongo import MongoClient
import logging

logger = logging.getLogger(__name__)


class NodeStorage:

    def __init__(self, db_addr='127.0.0.1', db_port=27017):
        self.session = MongoClient(db_addr, db_port)
        self.db = self.session.node_database
        self.nodes = self.db.node_collection

    def clear_db(self):
        """ Removes the full database """
        self.session.drop_database('node_database')

    def add(self, node):
        """ Adds a node to the database

        Args:
            node: A node Node object
        return:
            node_id: _id value of mongodb document
        """
        logger.info('adding node to the db: {}'.format(node))
        return self.nodes.insert_one(node).inserted_id

    def replace(self, node, upsert=False):
        """ Updates a node with the latest result

        Args:
            node: updated node (should include the db ID)
            upsert: If the node is not yet present in the db it will
                    add if if this is set to True
        """
        self.nodes.replace_one({'_id': node['_id']}, node)

    def get_nodes(self):
        """ Prints out all nodes """
        for item in self.nodes.find():
            print(item)

    def get_node(self, node_id):
        """ Returns a single node """
        print(self.nodes.find_one({"_id": ObjectId(node_id)}))


if __name__ == '__main__':
    node_storage = NodeStorage()
    node_storage.get_nodes()
