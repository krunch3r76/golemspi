# events/log_events/identity_event.py
from ..log_line import LogLine
from ..event import Event

import re


class IdentityEvent(Event):
    def __init__(self, timestamp, identity_address):
        self.identity_address = identity_address

    @classmethod
    def from_log_line(cls, log_line: LogLine):
        # [2023-07-25T23:40:14.623-0700 INFO  ya_identity::service::identity] using default identity: 0xac7b8d47107933fb3108b606f5299b742bdc2d6d

        # Define a regular expression pattern to find the address after "identity:"
        pattern = r"identity:\s+(?P<address>\S+)"

        # Use re.search to find the first occurrence of the pattern in the line
        match = re.search(pattern, log_line.message)

        if not match:
            return None

        address = match.group("address")

        return cls(log_line.timestamp, address)
