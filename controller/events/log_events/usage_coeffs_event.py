from ..log_line import LogLine
from ..event import Event

import re
import json
from collections import namedtuple

# Define the named tuple class
UsageCoeffs = namedtuple("UsageCoeffs", ["cpu_sec", "duration_sec"])


class UsageCoeffsEvent(Event):
    def __init__(self, timestamp, usage_coeffs: UsageCoeffs):
        super().__init__(timestamp)
        self.usage_coeffs = usage_coeffs

    @classmethod
    def from_log_line(cls, log_line: LogLine):
        """
        [2023-06-25T00:04:38.326-0700 INFO  ya_provider::market::provider_market] Creating offer for preset [vm] and ExeUnit [vm]. Usage coeffs: {"golem.usage.cpu_sec": 6.944444444444445e-6, "golem.usage.duration_sec": 1.388888888888889e-6}
        """

        pattern = r"Usage coeffs:\s+(\{.*?\})"
        match = re.search(pattern, string)

        if not match:
            return None

        coeffs_string = match.group(1)
        usage_coeffs_dict = json.loads(coeffs_string)
        # Convert the dictionary to a named tuple instance
        usage_coeffs = UsageCoeffs._make(usage_coeffs_dict.values())

        return cls(
            log_line.timestamp,
            usage_coeffs,
        )
