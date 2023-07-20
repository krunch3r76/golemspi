from ..event import Event
from ..log_line import LogLine
from ..log_events import InitializedPaymentAccountEvent


def identify_event_class(log_line: LogLine):
    if log_line.message.startswith("Initialised payment account"):
        return InitializedPaymentAccountEvent.from_log_line(log_line)
