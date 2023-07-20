# ./events/handlers/market_handler.py
from ..event import Event
from ..log_line import LogLine
from ..log_events import NewAgreementEvent


def identify_event_class(log_line: LogLine):
    # event_class = Event(log_line.timestamp)  # Identify the appropriate event class
    """
    [2023-05-28T08:05:05.879-0700 INFO  ya_provider::market::provider_market] Got agreement [c6b01ea71e758504139bfe40983618c457d1c76fb6d824d93651c9642293e2bd] from Requestor [0x33a6973df17ceae741b26f4372ee101cc81e82dd] for subscription [vm].
    """
    if log_line.message.startswith("Got agreement"):
        return NewAgreementEvent.from_log_line(log_line)
    return None
