from ..event import Event
from ..log_line import LogLine
from ..log_events import PaymentAccountsEvent, PaymentNetworkEvent, UsingSubnetEvent


def identify_event_class(log_line: LogLine):
    if log_line.message.startswith("Payment accounts: ["):
        return PaymentAccountsEvent.from_log_line(log_line)
    elif log_line.message.startswith("Using payment network:"):
        return PaymentNetworkEvent.from_log_line(log_line)
    elif log_line.message.startswith("Using subnet:"):
        return UsingSubnetEvent.from_log_line(log_line)
