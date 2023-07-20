from ..log_line import LogLine
from ..event import Event

import re


def strip_escape_codes(string):
    # Define the regex pattern for escape codes
    escape_pattern = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")

    # Remove escape codes from the string
    stripped_string = re.sub(escape_pattern, "", string)

    return stripped_string


class UsingSubnetEvent(Event):
    def __init__(self, timestamp, subnet):
        super().__init__(timestamp)
        self.subnet = subnet

    @classmethod
    def from_log_line(cls, log_line: LogLine):
        """
        [2023-06-25T00:04:38.323-0700 INFO  ya_provider::provider_agent] Using subnet: [38;5;184mpublic[0m
        """

        # Remove escape codes
        stripped_string = strip_escape_codes(log_line.message)

        # Extract the payment network value
        match = re.search(r":\s([^:]+)$", stripped_string)
        if not match:
            return None

        subnet = match.group(1).strip()

        return cls(log_line.timestamp, subnet)
