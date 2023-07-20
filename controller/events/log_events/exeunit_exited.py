# /controller/events/log_events/exeunit_exited.py

from ..log_line import LogLine
from ..event import Event

import re
from pathlib import Path


class ExeUnitExitedEvent(Event):
    def __init__(
        self,
        timestamp,
        exit_status_str,
        exit_status_code,
        agreement_hash,
        activity_hash,
    ):
        super().__init__(timestamp)
        self.exit_status_str = exit_status_str
        self.exit_status_code = exit_status_code
        self.agreement_hash = agreement_hash
        self.activity_hash = activity_hash

    @classmethod
    def from_log_line(cls, log_line: LogLine):
        """
        [2023-05-29T08:11:51.880-0700 INFO  ya_provider::execution::task_runner] ExeUnit process exited with status Finished - exit status: 0, agreement [db5506e88ff312070eca87147d445dc0ce6084723c3f41158e1f7b9e72ece679], activity [94ffdb99fcd4467ea489218a8ce3cb2a].
        """
        pattern = r"ExeUnit process exited with status (?P<exit_status_str>\w+) - exit status: (?P<exit_status_code>\d+), agreement \[(?P<agreement_hash>[\w]+)\], activity \[(?P<activity_hash>[\w]+)\]."

        match = re.search(pattern, log_line.message)
        if not match:
            return None

        exit_status_str = match.group("exit_status_str")
        exit_status_code = int(match.group("exit_status_code"))
        agreement_hash = match.group("agreement_hash")
        activity_hash = match.group("activity_hash")

        return cls(
            log_line.timestamp,
            exit_status_str,
            exit_status_code,
            agreement_hash,
            activity_hash,
        )
