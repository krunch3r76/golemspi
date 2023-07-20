# controller/events/handlers/payments_handler.py

from ..event import Event
from ..log_line import LogLine
from ..log_events import NewCostInformationEvent, FinalCostForActivityEvent


def identify_event_class(log_line: LogLine):
    """
    [2023-05-29T07:48:27.999-0700 INFO  ya_provider::payments::payments] Updating cost for activity [94ffdb99fcd4467ea489218a8ce3cb2a]: 0.000177839206922222, usage [2.008308, 118.002688984].

    [2023-05-29T05:03:34.338-0700 INFO  ya_provider::payments::payments] Final cost for activity [404ab06b846645c7ab1141be39bb4182]: 0.000019506929073611.
    """
    if log_line.message.startswith("Updating cost for activity"):
        return NewCostInformationEvent.from_log_line(log_line)
    elif log_line.message.startswith("Final cost for activity"):
        return FinalCostForActivityEvent.from_log_line(log_line)
    return None
