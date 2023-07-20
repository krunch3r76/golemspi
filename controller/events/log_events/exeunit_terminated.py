# /controller/events/log_events/exeunit_terminated.py

from ..log_line import LogLine
from ..event import Event

import re


class ExeUnitTerminatedEvent(Event):
    def __init__(self, timestamp, activity_hash):
        super().__init__(timestamp)
        self.activity_hash = activity_hash

    @classmethod
    def from_log_line(cls, log_line: LogLine):
        """
        [2023-05-29T08:11:51.880-0700 INFO  ya_provider::execution::task_runner] ExeUnit for activity terminated: [94ffdb99fcd4467ea489218a8ce3cb2a].
        """

        pattern = r"ExeUnit for activity terminated: \[(?P<activity_hash>[\w]+)\]."

        match = re.search(pattern, log_line.message)

        if not match:
            return None

        activity_hash = match.group("activity_hash")

        return cls(log_line.timestamp, activity_hash)
