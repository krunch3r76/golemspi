# /controller/events/log_events/new_exeunit_pid.py

from ..log_line import LogLine
from ..event import Event

import re
from pathlib import Path


class NewExeUnitPidEvent(Event):
    def __init__(self, timestamp, pid):
        super().__init__(timestamp)
        self.pid = pid

    @classmethod
    def from_log_line(cls, log_line):
        """
        [2023-05-29T01:21:06.646-0700 INFO  ya_provider::execution::exeunit_instance] Exeunit process spawned, pid: 486619
        """

        pattern = r"pid: (?P<pid>\d+)"
        match = re.search(pattern, log_line.message)

        if not match:
            return None

        pid = match.group("pid")

        # Create a new instance of NewExeunitPidEvent
        return cls(log_line.timestamp, pid)
