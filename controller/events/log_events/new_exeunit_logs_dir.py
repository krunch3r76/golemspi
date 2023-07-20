# /controller/events/log_events/new_exeunit_logs_dir.py

from ..log_line import LogLine
from ..event import Event

import re
from pathlib import Path


class NewExeUnitLogsDirEvent(Event):
    def __init__(self, timestamp, path_to_logs_dir, activity_hash):
        super().__init__(timestamp)
        self.path_to_logs_dir = path_to_logs_dir
        self.activity_hash = activity_hash

    @classmethod
    def from_log_line(cls, log_line):
        """
        [2023-05-29T01:21:06.645-0700 INFO  ya_provider::execution::exeunit_instance] Exeunit log directory: /home/golem/.local/share/ya-provider/exe-unit/work/a20c1e8861638bfd9120ba3088b270b6f2b33aae0fd6ad479ba6e81a0fbe9f00/225e48e33e2a4c429af6c836f1a29a8e/logs
        """

        pattern = r"log directory: (?P<path_to_logs_dir>.*)"
        match = re.search(pattern, log_line.message)

        if not match:
            return None

        path_to_logs_dir = match.group("path_to_logs_dir")

        # Extract the parent directory name using pathlib.Path
        activity_hash = Path(path_to_logs_dir).parent.name

        # Create a new instance of NewExeUnitLogsDirEvent
        return cls(log_line.timestamp, path_to_logs_dir, activity_hash)
