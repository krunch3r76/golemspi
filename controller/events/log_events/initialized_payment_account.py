from ..log_line import LogLine
from ..event import Event

import re


class InitializedPaymentAccountEvent(Event):
    def __init__(self, timestamp, mode, address, driver, network, token):
        super().__init__(timestamp)
        self.mode = mode
        self.address = address
        self.driver = driver
        self.network = network
        self.token = token

    @classmethod
    def from_log_line(cls, log_line: LogLine):
        """
        [2023-06-24T21:27:50.616-0700 INFO  ya_erc20_driver::driver::cli] Initialised payment account. mode=RECV, address=0x742a42f763b551a91994d64958e4475a739da2b4, driver=erc20, network=goerli, token=tGLM
        """
        # Define the regex pattern with named groups
        pattern = r"mode=(?P<mode>[^,]+), address=(?P<address>[^,]+), driver=(?P<driver>[^,]+), network=(?P<network>[^,]+), token=(?P<token>[^\s]+)"

        # Perform the regex search
        match = re.search(pattern, log_line.message)

        if not match:
            return None

        # Extract the named matches
        mode = match.group("mode")
        address = match.group("address")
        driver = match.group("driver")
        network = match.group("network")
        token = match.group("token")

        return cls(log_line.timestamp, mode, address, driver, network, token)
