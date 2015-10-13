#!/usr/bin/python3

from threading import Thread
import queue
import time
import logging
from probe_storage import ProbeStorage
from datetime import datetime


logger = logging.getLogger(__name__)


def pretty_time(timestamp):
    """ convert timestamp for pretty printing """
    return datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d %H:%M:%S')


class Poller:
    """ Poller Class is responsible for running
    and scheduling probes """

    def __init__(self, node_details):
        """ Initialising the probe_queue and probe_result_queue """
        self.node_details = node_details

        self._probe_queue = queue.Queue()
        self._probe_result_queue = queue.Queue()
        self.probe_storage = ProbeStorage()
        self.probe_list = []

    def __repr__(self):
        """ Print the current queue contents """
        if not self._probe_queue.empty():
            return "There's stuff in the probe queue"
        else:
            return "The probe queue is empty"

    def start(self):
        """ Start the probe manager

        run the main probe loop in a seperate thread """

        logger.info('Starting probe manager thread')
        self._manager_thread = Thread(target=self._poller)
        self._manager_thread.daemon = True
        self._manager_thread.start()

        logger.info('starting probe result thread')
        self._probe_result_thread = Thread(target=self._probe_result_handler)
        self._probe_result_thread.daemon = True
        self._probe_result_thread.start()

    def stop(self):
        """ Gracefully stops the poller """
        logger.info('Stopping poller...')

    def add(self, probe):
        """ Adds a new probe to the queue """

        if not probe.probe_id:
            logger.debug('Probe {} added to the database'
                         .format(probe.name))
            probe.probe_id = self.probe_storage.add(probe)

        if probe.probe_id not in self.probe_list:
            logger.debug('Probe {} added to the poller queue'
                         .format(probe.name))
            self._probe_queue.put(probe)
            self.probe_list.append(probe.probe_id)

    def _probe_result_handler(self):
        """ Handles received probe results """
        while True:
            while not self._probe_result_queue.empty():
                probe = self._probe_result_queue.get()
                print("Updating probe ID {}, "
                      "address {}, "
                      "run_at {}".format(probe.probe_id,
                                         probe.dest_addr,
                                         pretty_time(probe.run_at)))
                self.probe_storage.update(probe)

    def _poller(self):
        """ The probe event loop """

        while True:
            # First lets handle all the queued probes
            if not self._probe_queue.empty():
                current_probe = self._probe_queue.get()

                # Check if the probe should be run already
                # If not, add it to the back of the queue
                if current_probe.run_at <= time.time():
                    result = current_probe.run()
                    if result:
                        self._probe_result_queue.put(current_probe)

                    if current_probe.reschedule():
                        # reschedule the probe if needed
                        self._probe_queue.put(current_probe)
                else:
                    self._probe_queue.put(current_probe)
