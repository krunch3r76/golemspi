from ..log_line import LogLine
from ..event import Event

import re


class HardwareResourcesCapEvent(Event):
    def __init__(self, timestamp, cpu_threads, mem_gib, storage_gib):
        super().__init__(timestamp)
        self.cpu_threads = cpu_threads
        self.mem_gib = mem_gib
        self.storage_gib = storage_gib

    @classmethod
    def from_log_line(cls, log_line: LogLine):
        """
        [2023-06-25T00:04:38.322-0700 INFO  ya_provider::hardware] Hardware resources cap: Resources { cpu_threads: 31, mem_gib: 42.753664404153824, storage_gib: 336.6809295654297 }
        """
        pattern = r"cpu_threads:\s(?P<cpu_threads>\d+),\s+mem_gib:\s(?P<mem_gib>[\d.]+),\s+storage_gib:\s(?P<storage_gib>[\d.]+)"

        match = re.search(pattern, log_line.message)

        if not match:
            print("no match")
            print(log_line.message)
            return None

        cpu_threads = int(match.group("cpu_threads"))
        mem_gib = float(match.group("mem_gib"))
        storage_gib = float(match.group("storage_gib"))

        return cls(log_line.timestamp, cpu_threads, mem_gib, storage_gib)
