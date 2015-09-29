#!/usr/bin/env python3

import asyncio
import logging
from node_connector import MessageHandler, ConnectionProtocol


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
