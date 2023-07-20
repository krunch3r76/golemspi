from ..log_line import LogLine
from ..event import Event

import re


class PaymentAccountsEvent(Event):
    def __init__(self, timestamp, accounts):
        super().__init__(timestamp)
        self.accounts = accounts

    @classmethod
    def from_log_line(cls, log_line: LogLine):
        """
        [2023-06-25T00:04:36.872-0700 INFO  ya_provider::provider_agent] Payment accounts: [
            AccountView {
                address: 0x742a42f763b551a91994d64958e4475a739da2b4,
                network: Mumbai,
                platform: "erc20-mumbai-tglm",
            },
            AccountView {
                address: 0x742a42f763b551a91994d64958e4475a739da2b4,
                network: Goerli,
                platform: "erc20-goerli-tglm",
            },
            AccountView {
                address: 0x742a42f763b551a91994d64958e4475a739da2b4,
                network: Rinkeby,
                platform: "erc20-rinkeby-tglm",
            },
            AccountView {
                address: 0x742a42f763b551a91994d64958e4475a739da2b4,
                network: Rinkeby,
                platform: "zksync-rinkeby-tglm",
            },
        ]
        """

        # Define the regular expression pattern
        pattern = r"address:\s(?P<address>.*?),\s+network:\s(?P<network>.*?),\s+platform:\s\"(?P<platform>.*?)\""

        # Find all matches in the string using the regular expression pattern
        matches = re.findall(pattern, log_line.message)

        if not matches:
            return None

        # Create a list of dictionaries from the matches
        account_list = [
            {"address": match[0], "network": match[1], "platform": match[2]}
            for match in matches
        ]

        return cls(log_line.timestamp, account_list)
