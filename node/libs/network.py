#!/usr/bin/env python

# This library provides a design pattern based on the
# publish-subscribe model.
#
# Further reading:
# http://www.slideshare.net/ishraqabd/publish-subscribe-model-overview-13368808

import json
import queue
import socket


class NodeControllerClient:
    """ TODO: Create a interface layer class
    to be able to exchange traffic with the message
    handler. The idea is that we have options for
    serial and socket interfaces """

    def __init__(self, controller_address, controller_port):
        self.controller_addr = controller_address
        self.controller_port = controller_port

    def register(self):
        """ Registers to the controller """

        self.protocol = ClientTcpProtocol(self.controller_addr,
                                          self.controller_port)
        print("Registering to controller {}:{}".format(self.controller_addr,
                                                       self.controller_port))
        message = {'type': 'register',
                   'ip_addr': ['127.0.0.1'],
                   'mac': 'aa:bb:cc:dd:ee:ff',
                   'last_registered': None,
                   'last_node_id': None,
                   'shared_key': 'public'}
        self.protocol.send_message(message)
        reply = self.protocol.recv_message()
        return reply

    def heartbeat(self):
        """ Sends a heartbeat message to the controller

        sends a message type PING. We expect a similar message
        back from the controller
        """
        self.protocol.send_message({'type': 'PING'})

    def probe_result(self, result):
        self.protocol.send_message(result)


class ClientTcpProtocol:
    """ A generic socket class that can be used by the NodeControllerClient

    This doesn't use asyncio to keep the clients simple.
    hopefully by having the various clients as completely
    seperate programs we won't need any multiprocessing
    or threading but rather leave it to the OS to handle
    """

    def __init__(self, hub_address, hub_port):
        """ Set up the TCP connection to the pubsub Hub """
        self.recv_queue = queue.Queue()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((hub_address, hub_port))
        self.sock.setblocking(0)

    def send_message(self, message):
        """ Sends a message to the pubsub Hub

        The type of message should be handled by the Publisher
        and Subscriber classes
        """
        message = (json.dumps(message) + "\r\n").encode('ascii')
        try:
            self.sock.send(message)
        except BlockingIOError:
            # This gets raised when the send queue is full
            print("Send buffer full, can't send message {}".format(message))

    def recv_message(self):
        """ Returns a message received from the controller

        data is stored into a buffer. It will try to find a full
        message (demarked by \r\n) and add it to the recv queue.
        """

        try:
            buff = (self.sock.recv(1024)).decode('ascii')
            self.recv_queue.put(json.loads(buff.strip()))
        except BlockingIOError:
            pass

        if not self.recv_queue.empty():
            return self.recv_queue.get_nowait()
        else:
            return None

    def close(self):
        """ Closes the socket connection """
        self.sock.close()


if __name__ == '__main__':
    pass
