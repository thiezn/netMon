#!/usr/bin/env python3

import asyncio
import json
import logging
from node_storage import NodeStorage


class ConnectionProtocol(asyncio.Protocol):
    """ A Connection protocol listening for messages from nodes """

    def __init__(self, message_handler, node):
        """ Connector mediates between the node and the Protocol.
        Node is the local node on the network that handles incoming
        messages """
        self._message_handler = message_handler
        self._node = node
        self._recv_buffer = ''

    def message_received(self, msg):
        """ Process the raw data with the message_handler and local node

        TODO: What are we going to do with the Data? We should
        store the received probe data in a database probably. Do
        we need to acknowledge we received the data? I guess not?

        Maybe we can use this same server for synchronising configuration
        data and send periodic keepalives?

        Have to describe a header, or at least a json/dict standard for
        messages.

        The actual code for handling messages reside in the message_handler
        class, in this case the Controller. This function should determine the
        right message type and call the message_handler function to handle the
        data
        """
        if msg['type'] == 'register':
            self._message_handler.register(self.peername, msg)
        if msg['type'] == 'unregister':
            self._message_handler.unregister(self.peername, msg)
        if msg['type'] == 'probe':
            result = self._message_handler.probe(self.peername, msg)
            if result:
                self.send_msg(result)

    def connection_made(self, transport):
        """ Called when connection is initiated to this node """

        self.transport = transport
        self.peername = self.transport.get_extra_info('peername')
        logging.info('connection from {} '.format(self.peername))

    def connection_lost(self, exc):
        # Make sure we unregister a node when a connection
        # is terminated due to an exception
        if not exc:
            exc = "Connection reset by peer"
        self._message_handler.unregister(self.peername, exc)

    def data_received(self, data):
        """ The protocol expects a json message containing
        the following fields:

            type:       register/unregister/probe/bla
            args*:      Whatever data the type requires
        """

        self._recv_buffer += data.decode('utf-8')

        # check if we received a full message
        # if so, remove the message from the buffer and pass msg along
        if '\r\n' in self._recv_buffer:
            message, _, self._recv_buffer = self._recv_buffer.partition('\r\n')
            self.message_received(json.loads(message))

    def send_msg(self, data):
        """ This function takes a dictionary
        and serializes it to a message ready to send

        Spaces are removed from the JSON data to conserve bytes. The
        message is terminated by line feed (\r\n) """

        message = json.dumps(data, separators=(',', ':')) + "\r\n"
        self.transport.write(message.encode('utf-8'))


class MessageHandler:
    def __init__(self, name="MyMessageHandler"):
        """ MessageHandler of remote nodes

        Nodes register to a MessageHandler and send their
        probe results for processing.

        The MessageHandler requires an underlying transport/protocol
        implementation to provide the low level send and
        receive of messages.

        TODO: provide a way to exchange data between
        multiple Controller's. This would allow for a
        greater distributed architecture.
        """
        self.name = name
        self.nodes = []
        self.version = '0.1'
        self.node_storage = NodeStorage()

    def _update_console(self):
        """ Call this function to update the terminal window output """
        print("Connected nodes: {}         ".format(len(self.nodes)), end='\r')

    def register(self, peername, msg):
        """ Registers a node to the controller

        Only accepting connection if software versions match """

        if self.version != msg['version']:
            logging.debug("Registration of node {} denied due to "
                          "version mismatch".format(peername))
            return {'type': 'register', 'error': 'VERSION_MISMATCH'}

        node = {}
        node['peername'] = peername
        node['name'] = msg['name']
        node['version'] = msg['version']
        node['group'] = msg['group']
        node['is_connected'] = True

        node_in_db = self.node_storage.get_node_by_name(node['name'])
        if node_in_db:
            # Update any potential changed parameters in db
            node['_id'] = node_in_db['_id']
            self.node_storage.replace(node)  # updates any changed data
        else:
            # This is a unknown node, lets store it in db
            node['_id'] = self.node_storage.add(node)

        self.nodes.append(node)
        logging.info('Node {} wants to register'.format(node))
        logging.info('Node {} sent the following: {}'.format(node, msg))
        logging.debug('Connected nodes are now {}'.format(self.nodes))
        self._update_console()

    def unregister(self, peername, msg=None):
        """ Unregisters a node from the controller """

        for node in self.nodes:
            if node['peername'] == peername:
                node['is_connected'] = False
                self.node_storage.replace(node)
                self.nodes.remove(node)
                logging.info('Unregistering client {}, reason {}'
                             .format(node, msg))
                logging.info('Connected nodes: {}'.format(self.nodes))
                break

        self._update_console()

    def probe(self, node, msg):
        logging.info('Node {} sent probe result: {}'.format(node, msg))
        return {'type': 'probe', 'data': 'received probe, thanks!'}


def main():
    logging.basicConfig(filename='log.tcp_server',
                        level=logging.DEBUG,
                        filemode='w',
                        format='%(asctime)s %(levelname)s %(message)s')

    logging.info('Initialising the Message Handler service')
    message_handler = MessageHandler()
    loop = asyncio.get_event_loop()
    # Each client will create a new protocol instance
    coro = loop.create_server(lambda: ConnectionProtocol(message_handler,
                                                         loop),
                              '127.0.0.1', 10666)
    server = loop.run_until_complete(coro)

    # Serve requests until Ctrl+C
    logging.info('Serving on {}'.format(server.sockets[0].getsockname()))
    print('Serving on {}'.format(server.sockets[0].getsockname()))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    # Close the server
    try:
        server.close()
        loop.until_complete(server.wait_closed())
        loop.close()
    except:
        pass

if __name__ == '__main__':
    main()
