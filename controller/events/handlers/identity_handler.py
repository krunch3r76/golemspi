from ..log_line import LogLine
from ..log_events import IdentityEvent


def identify_event_class(log_line: LogLine):
    if "identity: " in log_line.message:
        return IdentityEvent.from_log_line(log_line)
