# /controller/events/log_events/final_cost_for_activity.py

from ..log_line import LogLine
from ..event import Event

import re


class FinalCostForActivityEvent(Event):
    def __init__(self, timestamp, activity_hash, final_cost):
        super().__init__(timestamp)
        self.activity_hash = activity_hash
        self.final_cost = final_cost

    @classmethod
    def from_log_line(cls, log_line: LogLine):
        """
        [2023-05-29T05:03:34.338-0700 INFO  ya_provider::payments::payments] Final cost for activity [404ab06b846645c7ab1141be39bb4182]: 0.000019506929073611.
        """

        pattern = r"Final cost for activity \[(?P<activity_hash>\w+)\]: (?P<final_cost>\d+\.\d+)"
        match = re.search(pattern, log_line.message)

        if not match:
            return None

        activity_hash = match.group("activity_hash")
        final_cost = match.group("final_cost")

        return cls(log_line.timestamp, activity_hash, final_cost)
