# /controllers/events/log_events/new_cost_information.py


from ..log_line import LogLine
from ..event import Event

import re
from pathlib import Path


class NewCostInformationEvent(Event):
    def __init__(self, timestamp, activity_hash, cost, usage_vector):
        super().__init__(timestamp)
        self.activity_hash = activity_hash
        self.cost = cost
        self.usage_vector = usage_vector

    @classmethod
    def from_log_line(cls, log_line):
        """
        [2023-05-29T07:48:27.999-0700 INFO  ya_provider::payments::payments] Updating cost for activity [94ffdb99fcd4467ea489218a8ce3cb2a]: 0.000177839206922222, usage [2.008308, 118.002688984].
        """

        pattern = r"Updating cost for activity \[(?P<activity>[\w]+)\]: (?P<cost>[\d.]+), usage \[(?P<usage>[\d., ]+)\]."

        match = re.search(pattern, log_line.message)

        if not match:
            return None

        activity_hash = match.group("activity")
        cost = float(match.group("cost"))
        usage_vector = [float(num) for num in match.group("usage").split(",")]

        # Create a new instance of NewCostInformationEvent
        return cls(log_line.timestamp, activity_hash, cost, usage_vector)
