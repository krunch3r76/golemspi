# events/log_events/new_agreement_event.py

from ..log_line import LogLine
from ..event import Event

import re


class NewAgreementEvent(Event):
    def __init__(self, timestamp, agreement_hash, requestor_address, subscription):
        super().__init__(timestamp)
        self.timestamp = timestamp
        self.agreement_hash = agreement_hash
        self.requestor_address = requestor_address
        self.subscription = subscription

    @classmethod
    def from_log_line(cls, log_line):
        """
        [2023-05-28T08:05:05.879-0700 INFO  ya_provider::market::provider_market] Got agreement [c6b01ea71e758504139bfe40983618c457d1c76fb6d824d93651c9642293e2bd] from Requestor [0x33a6973df17ceae741b26f4372ee101cc81e82dd] for subscription [vm].
        log_line.message = Got agreement [c6b01ea71e758504139bfe40983618c457d1c76fb6d824d93651c9642293e2bd] from Requestor [0x33a6973df17ceae741b26f4372ee101cc81e82dd] for subscription [vm].
        """
        # Define the regex pattern
        pattern = r"Got agreement \[([\w]+)\] from Requestor \[([\w]+)\] for subscription \[([\w]+)\]"

        # Extract the desired values using regex
        match = re.search(pattern, log_line.message)
        if match:
            agreement_hash = match.group(1)
            requestor_address = match.group(2)
            subscription = match.group(3)

            # Create a new instance of NewAgreementEvent
            return cls(
                log_line.timestamp, agreement_hash, requestor_address, subscription
            )

        # Return None if the pattern does not match
        return None
