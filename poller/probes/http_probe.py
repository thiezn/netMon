#!/usr/bin/env python3

import probes
import requests
from time import time


class HttpProbe(probes.Probe):
    """ Runs a HTTP probe to the provided destination """

    def __init__(self, dest_url, *args, **kwargs):
        """ Making sure to pass on the scheduling variables to the
        main probe.

        Args:
            count: amount of icmp probes to send
            preload: amount of probes to send simultaneously
            timeout: amount of seconds before a probe times out
        """

        super().__init__(*args, **kwargs)
        self.dest_url = dest_url
        self.session = requests.session()

    def db_record(self):
        """ Should return what we want to write to the
        database """
        return {"probe_id": self.probe_id,
                "type": self.name,
                "recurrence_time": self.recurrence_time,
                "recurrence_count": self.recurrence_count,
                "run_at": self.run_at,
                "run_on_nodes": self.run_on_nodes,
                "run_on_groups": self.run_on_groups,
                "dest_url": self.dest_url,
                "status_code": self.status_code,
                "call_duration": self._call_duration}

    def run(self):
        return self.http_get()

    def http_get(self):
        """ Runs a http GET requests


        Returns:
            page: The returned HTML page
        """

        _start_time = time()
        response = self.session.get(self.dest_url)
        self._call_duration = time() - _start_time
        self.status_code = response.status_code

        if response.status_code == 200:
            return True
        else:
            return False


if __name__ == '__main__':
    probe = HttpProbe('http://www.mortimer.nl/')
    probe.run()
    print(probe.db_record())


    probe = HttpProbe('http://85.119.21.16')
    probe.run()
    print(probe.db_record())
