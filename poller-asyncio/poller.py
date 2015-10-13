#!/usr/bin/env python3

# Taken from documentation example on subprocesses:
# https://docs.python.org/3/library/asyncio-subprocess.html chapter 18.5.6.7
# http://stackoverflow.com/questions/29324346/how-do-i-connect-asyncio-coroutines-that-continually-produce-and-consume-data

import asyncio
import logging


class ProbeProtocol(asyncio.SubprocessProtocol):
    def __init__(self, exit_future):
        self.output = bytearray()
        self.exit_future = exit_future

    def pipe_data_received(self, fd, data):
        self.output.extend(data)

    def process_exited(self):
        self.exit_future.set_result(True)


class Poller:
    def __init__(self, loop):
        self.probe_queue = asyncio.Queue()
        self.probe_results = asyncio.Queue()
        self.flag = asyncio.Event()
        self.loop = loop

    async def start(self):
            exit_future = asyncio.Future(loop=self.loop)
            # Create the subprocess controlled by the protocol DateProtocol,
            # redirect the standard output into a pipe
            probe = self.loop.subprocess_exec(lambda: ProbeProtocol(exit_future),
                                              'ping', '8.8.8.8', '-c 1',
                                              stdin=None, stderr=None)
            transport, protocol = await probe
            # Wait for the subprocess exit using the process_exited() method
            # of the protocol
            await exit_future

            transport.close()

            # Read the output which was collected by the pipe_data_received()
            # method of the protocol
            data = bytes(protocol.output)
            self.probe_results.put(data.decode('utf-8').rstrip())

    async def read(self):
        return (await self.probe_results.get())


async def reporter(probe):
    while True:
        result = await probe.read()
        print("probe result: {}".format(result))


def main():
    logging.basicConfig(filename='log.poller',
                        level=logging.DEBUG,
                        filemode='w',
                        format='%(asctime)s %(levelname)s %(message)s')

    logging.info('Initialising the poller...')
    loop = asyncio.get_event_loop()
    poller = Poller(loop)
    loop.run_until_complete(poller.start())

    loop.run_forever()
    loop.close()

if __name__ == '__main__':
    main()
