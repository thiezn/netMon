#!/usr/bin/env python3

import time


class Probe:
    """ Class describing a Probe for use in the ProbeManager

    Args:
        run_at: when should the probe run, use "now" for a immediate probe
        recurrence_time: after how many seconds should the probe re-occur
        recurrence_count: how often should the probe re-occur
    """

    def __init__(self, *args, **kwargs):
        """ Define the probe name, set the run at time and define
         recurrence if any

        kwargs:
            run_at: when should the probe run, use "now" for a immediate probe
            recurrence_time: after how many seconds should the probe reoccur
            recurrence_count: how often should the probe reoccur
        """

        run_at = kwargs.get('run_at', None)
        recurrence_time = kwargs.get('recurrence_time', None)
        recurrence_count = kwargs.get('recurrence_count', None)
        self.run_on_nodes = kwargs.get('run_on_nodes', [])
        self.run_on_groups = kwargs.get('run_on_groups', [])
        self.probe_id = kwargs.get('probe_id', None)

        if recurrence_count and not recurrence_time:
            raise ValueError('Can\'t create recurring probe without '
                             'providing recurrence_count')

        if not run_at:
            self.run_at = time.time()
        else:
            self.run_at = run_at

        self.name = self.__class__.__name__
        self.recurrence_time = recurrence_time
        self.recurrence_count = recurrence_count

    def db_record(self):
        """ Should return what we want to write to the
        database """
        return {"type": self.name,
                "recurrence_time": self.recurrence_time,
                "recurrence_count": self.recurrence_count,
                "run_at": self.run_at,
                "run_on_nodes": self.run_on_nodes,
                "run_on_groups": self.run_on_groups}

    def reschedule(self):
        """ Check if the Probe has to reoccur again

        This should be run by the probe_manager class each time
        it has run a Probe that has the potential to be run again
        """

        if self.recurrence_time and not self.recurrence_count:
            # persistent reoccuring probe
            self.run_at += self.recurrence_time
            return True
        elif self.recurrence_time and self.recurrence_count > 1:
            # no persistent reoccuring probe
            self.run_at += self.recurrence_time
            self.recurrence_count -= 1
            return True
        else:
            # one off probe
            return False

    def run(self):
        """ Runs the specified probe
        each probe type has to overload this function """
        raise NotImplementedError
