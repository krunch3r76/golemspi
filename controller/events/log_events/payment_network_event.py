from ..log_line import LogLine
from ..event import Event

import re


def strip_escape_codes(string):
    # Define the regex pattern for escape codes
    escape_pattern = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")

    # Remove escape codes from the string
    stripped_string = re.sub(escape_pattern, "", string)

    return stripped_string


class PaymentNetworkEvent(Event):
    def __init__(self, timestamp, payment_network):
        super().__init__(timestamp)
        self.payment_network = payment_network

    @classmethod
    def from_log_line(cls, log_line: LogLine):
        """
        [2023-06-25T00:04:38.322-0700 INFO  ya_provider::provider_agent] Using payment network: [36mrinkeby[0m
        [2023-06-25T00:04:38.322-0700 INFO  ya_provider::provider_agent] Using payment network: [36mmumbai[0m
        [2023-06-25T00:04:38.322-0700 INFO  ya_provider::provider_agent] Using payment network: [36mgoerli[0m
        """
        # Remove escape codes
        stripped_string = strip_escape_codes(log_line.message)

        # Extract the payment network value
        match = re.search(r":\s([^:]+)$", stripped_string)
        if not match:
            return None

        payment_network = match.group(1).strip()

        return cls(log_line.timestamp, payment_network)
