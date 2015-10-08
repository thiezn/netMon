#!/usr/bin/env python

# Library providing the TCP client that connects to the TCP server
# running on the controller node.

import json
import queue
import socket
from time import sleep
import logging

logger = logging.getLogger(__name__)


class MessageHandler:
    """ Handles send/recv messages from the ConnectionProtocol class.
    task_manager uses this to handle tasks """

    def __init__(self, controller_address, controller_port):
        self.controller_addr = controller_address
        self.controller_port = controller_port
        self.is_connected = False

    def register(self, node_details):
        """ Registers to the controller """

        logger.info("Registering to controller {}:{}"
                    .format(self.controller_addr, self.controller_port))
        self.protocol = ConnectionProtocol(self.controller_addr,
                                           self.controller_port)
        self.is_connected = True
        message = {'type': 'register',
                   'name': node_details['name'],
                   'version': node_details['version'],
                   'group': node_details['group'],
                   'ip_addr': ['127.0.0.1'],
                   'mac': 'aa:bb:cc:dd:ee:ff',
                   'last_registered': None,
                   'last_node_id': None,
                   'shared_key': 'public'}
        self.protocol.send_message(message)

    def unregister(self, node_details):
        """ Unregisters from the controller """

        logger.info("Unregistering from controller {}:{}"
                    .format(self.controller_addr, self.controller_port))
        message = {'type': 'unregister',
                   'name': node_details['name']}
        self.protocol.send_message(message)
        self.protocol.close()
        self.is_connected = False

    def heartbeat(self):
        """ Sends a heartbeat message to the controller

        sends a message type PING. We expect a similar message
        back from the controller
        """
        self.protocol.send_message({'type': 'PING'})

    def probe(self, message):
        self.protocol.send_message(message)


class ConnectionProtocol:
    """ A generic socket class that can be used by the MessageHandler

    This doesn't use asyncio to keep the clients simple.
    hopefully by having the various clients as completely
    seperate programs we won't need any multiprocessing
    or threading but rather leave it to the OS to handle
    """

    def __init__(self, server_address, server_port):
        """ Set up the TCP connection to the controller node """
        self._recv_buffer = ''

        self.recv_queue = queue.Queue()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while True:
            try:
                self.sock.connect((server_address, server_port))
                break
            except ConnectionRefusedError:
                print("Could not connect to server {}:{}. Retrying in 2 sec"
                      .format(server_address, server_port))
                sleep(2)

        self.sock.setblocking(0)

    def send_message(self, message):
        """ Sends a message to the controller node """

        message = json.dumps(message) + '\r\n'
        try:
            self.sock.send(message.encode('utf-8'))
        except BlockingIOError:
            # This gets raised when the send queue is full
            logger.debug("Send buffer full, can't send message {}"
                         .format(message))

    def recv_message(self):
        """ Returns a message received from the controller

        data is stored into a buffer. It will try to find a full
        message (demarked by \r\n) and add it to the recv queue.
        """

        try:
            self._recv_buffer += (self.sock.recv(1024)).decode('utf-8')
        except BlockingIOError:
            pass

        # check if we received a full message
        # if so, remove the message from the buffer and pass msg along
        if '\r\n' in self._recv_buffer:
            message, _, self._recv_buffer = self._recv_buffer.partition('\r\n')
            self.recv_queue.put(json.loads(message))

        """
        old code
        try:
            buff = (self.sock.recv(1024)).decode('utf-8')
            self.recv_queue.put(json.loads(buff.strip()))
        except BlockingIOError:
            pass
        """

    def close(self):
        """ Closes the socket connection """
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()


if __name__ == '__main__':
    pass
