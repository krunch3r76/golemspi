# events/log_line.py
from dataclasses import dataclass


# [2023-05-28T08:05:05.879-0700 INFO  ya_provider::market::provider_market] Got agreement [c6b01ea71e758504139bfe40983618c457d1c76fb6d824d93651c9642293e2bd] from Requestor [0x33a6973df17ceae741b26f4372ee101cc81e82dd] for subscription [vm].
@dataclass
class LogLine:
    raw_contents: str
    timestamp: str
    loglevel: str
    namespace: str
    message: str


def parse_log_line(log_line: str) -> LogLine:
    try:
        close_bracket_index = log_line.index("]")
        header = log_line[0:close_bracket_index]
        timestamp, loglevel, namespace = header[1:].split()
        timestamp = timestamp.strip()
        loglevel = loglevel.strip()
        namespace = namespace.strip()

        message_start_index = log_line.find("] ", close_bracket_index) + 1
        message = log_line[message_start_index:].strip()

    except ValueError:
        timestamp = None
        loglevel = None
        namespace = None
        message = log_line[log_line.find("]") + 1 :].strip()

    return LogLine(log_line, timestamp, loglevel, namespace, message)
