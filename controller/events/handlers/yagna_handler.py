from ..event import Event
from ..log_line import LogLine
from ..log_events import YagnaServiceStartedEvent


def identify_event_class(log_line: LogLine):
    if log_line.message.startswith("Starting yagna service!"):
        return YagnaServiceStartedEvent.from_log_line(log_line)
