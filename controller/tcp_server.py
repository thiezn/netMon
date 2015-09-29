#!/usr/bin/env python3

import asyncio
import json
import logging


class ConnectionProtocol(asyncio.Protocol):
    """ A Connection protocol listening for messages from nodes """

    def __init__(self, connector, node):
        """ Connector mediates between the node and the Protocol.
        Node is the local node on the network that handles incoming
        messages """
        self._connector = connector
        self._node = node

    def message_received(self, msg):
        """ Process the raw data with the connector and local node

        TODO: What are we going to do with the Data? We should
        store the received probe data in a database probably. Do
        we need to acknowledge we received the data? I guess not?

        Maybe we can use this same server for synchronising configuration
        data and send periodic keepalives?

        Have to describe a header, or at least a json/dict standard for
        messages.

        The actual code for handling messages reside in the connector class,
        in this case the Controller. This function should determine the
        right message type and call the connector function to handle the data
        """
        if msg['type'] == 'register':
            self._connector.register(self.peername, msg)
        if msg['type'] == 'probe':
            self._connector.probe_result(self.peername, msg)

    def connection_made(self, transport):
        """ Called when connection is initiated to this node """

        self.transport = transport
        self.peername = self.transport.get_extra_info('peername')
        print("connection from {}".format(self.peername))
        logging.info('connection from {} '.format(self.peername))

    def data_received(self, data):
        """ The protocol expects a json message containing
        the following fields:

            type:       subscribe/unsubscribe
            channel:    the name of the channel

        Upon receiving a valid message the protocol registers
        the client with the pubsub hub. When succesfully registered
        we return the following json message:
        """
        # TODO: have to create a message buffer, splitting messages with \r\n
        # For now assume we only receive one liners

        self.message_received(json.loads(data.decode("utf-8")))

    def send_msg(self, data):
        """ This function takes a dictionary
        and serializes it to a message ready to send

        Spaces are removed from the JSON data to conserve bytes. The
        message is terminated by line feed (\r\n) """

        message = json.dumps(data, separators=(',', ':')) + "\r\n"
        return message.encode('utf-8')


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

    def register(self, node, msg):

        if self.version != msg['version']:
            logging.debug("Registration of node {} denied due to "
                          "version mismatch".format(node))
            return {'type': 'register', 'error': 'VERSION_MISMATCH'}

        self.nodes.append(node)
        logging.info('Client {} wants to register'.format(node))
        logging.info('Client sent the following: {}'.format(msg))
        logging.debug('Connected nodes are now {}'.format(self.nodes))

    def probe_result(self, node, msg):
        logging.info('Node {} sent probe result: {}'.format(node, msg))


def main():
    logging.basicConfig(filename='log.message_handler',
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
