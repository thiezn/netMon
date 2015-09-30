#!/usr/bin/env python

# Library providing the TCP client that connects to the TCP server
# running on the controller node.

import json
import queue
import socket


class MessageHandler:
    """ Handles send/recv messages from the ConnectionProtocol class.
    task_manager uses this to handle tasks """

    def __init__(self, controller_address, controller_port):
        self.controller_addr = controller_address
        self.controller_port = controller_port
        self.is_connected = False

    def register(self):
        """ Registers to the controller """

        self.protocol = ConnectionProtocol(self.controller_addr,
                                           self.controller_port)
        print("Registering to controller {}:{}".format(self.controller_addr,
                                                       self.controller_port))
        self.is_connected = True
        message = {'type': 'register',
                   'version': '0.1',
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


class ConnectionProtocol:
    """ A generic socket class that can be used by the MessageHandler

    This doesn't use asyncio to keep the clients simple.
    hopefully by having the various clients as completely
    seperate programs we won't need any multiprocessing
    or threading but rather leave it to the OS to handle
    """

    def __init__(self, hub_address, hub_port):
        """ Set up the TCP connection to the controller node """
        self.recv_queue = queue.Queue()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((hub_address, hub_port))
        self.sock.setblocking(0)

    def send_message(self, message):
        """ Sends a message to the controller node """

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
