from ..event import Event
from ..log_line import LogLine
from ..log_events import UsageCoeffsEvent


def identify_event_class(log_line: LogLine):
    if log_line.message.startswith("Creating offer for preset"):
        return UsageCoeffsEvent.from_log_line(log_line)
