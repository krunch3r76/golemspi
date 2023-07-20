from ..event import Event
from ..log_line import LogLine
from ..log_events import HardwareResourcesCapEvent


def identify_event_class(log_line: LogLine):
    if log_line.message.startswith("Hardware resources cap:"):
        return HardwareResourcesCapEvent.from_log_line(log_line)
