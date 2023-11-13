from ..log_line import LogLine
from ..event import Event

import re
import json


class OfferFromPresetEvent(Event):
    def __init__(self, timestamp, name, offer):
        super().__init__(timestamp)
        self.name = name
        self.offer = offer

    @classmethod
    def from_log_line(cls, log_line: LogLine):
        """
        [2023-11-12T21:24:48.078-0800 INFO  ya_provider::market::provider_market] Offer for preset: vm = {
        """
        match = re.search(r"preset:\s+(\w+)", log_line.message)

        if not match:
            return None

        name = match.group(1)
        offer_dict = json.loads(log_line.message[log_line.message.index("{") :])

        return cls(log_line.timestamp, name, offer_dict)
