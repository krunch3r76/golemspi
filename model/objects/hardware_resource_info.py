from dataclasses import dataclass
from decimal import Decimal


@dataclass
class HardwareResourceInfo:
    timestamp: int
    cpu_threads: int
    mem_gib: Decimal
    storage_gib: Decimal

    def __post_init__(self):
        self.mem_gib = str(self.mem_gib)
        self.storage_gib = str(self.storage_gib)
