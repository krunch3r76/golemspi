# controller/events/log_events/yagna_service_started.py
from ..log_line import LogLine
from ..event import Event

import re


class YagnaServiceStartedEvent(Event):
    def __init__(self, timestamp, version, commit, build_date, build_number):
        super().__init__(timestamp)
        self.version = version
        self.commit = commit
        self.build_date = build_date
        self.build_number = build_number

    @classmethod
    def from_log_line(cls, log_line: LogLine):
        """
        [2023-06-24T21:27:18.207-0700 INFO  yagna] Starting yagna service! Version: 0.12.2 (8efd8657 2023-06-06 build #296).
        """
        # pattern = r"Starting yagna service! Version: (?P<version>[\d.]+) \((?P<commit>\w+) (?P<build_date>\d{4}-\d{2}-\d{2}) build #(?P<build_number>\d+)\)"
        pattern = r"Version: (?P<version>[\d.]+) \((?P<commit>\w+) (?P<build_date>\d{4}-\d{2}-\d{2}) build #(?P<build_number>\d+)\)"

        match = re.search(pattern, log_line.message)

        if not match:
            return None

        version = match.group("version")
        commit = match.group("commit")
        build_date = match.group("build_date")
        build_number = match.group("build_number")

        return cls(log_line.timestamp, version, commit, build_date, build_number)
