# events/event_handler.py

from .log_line import LogLine, parse_log_line
import controller.events.handlers.market_handler as market_handler
import controller.events.handlers.execution_handler as execution_handler
import controller.events.handlers.payments_handler as payments_handler
import controller.events.handlers.yagna_handler as yagna_handler
import controller.events.handlers.driver_handler as driver_handler
import controller.events.handlers.provider_agent_handler as provider_agent_handler
import controller.events.handlers.hardware_handler as hardware_handler


def determine_event_type_and_data(log_line: LogLine):
    # logic to determine event type and associated data
    event_class = None
    if log_line.namespace == "yagna":
        event_class = yagna_handler.identify_event_class(log_line)
    elif "::driver::" in log_line.namespace:
        event_class = driver_handler.identify_event_class(log_line)
        event_class = driver_handler.identify_event_class(log_line)
    elif log_line.namespace.startswith("ya_provider::provider_agent"):
        event_class = provider_agent_handler.identify_event_class(log_line)
    elif log_line.namespace.startswith("ya_provider::hardware"):
        event_class = hardware_handler.identify_event_class(log_line)
    elif log_line.namespace.startswith("ya_provider::market"):
        event_class = market_handler.identify_event_class(log_line)
    elif log_line.namespace.startswith("ya_provider::execution"):
        event_class = execution_handler.identify_event_class(log_line)
    elif log_line.namespace.startswith("ya_provider::payments"):
        event_class = payments_handler.identify_event_class(log_line)
    else:
        event_class = None
    # determine the event type based on the log_line
    return event_class
