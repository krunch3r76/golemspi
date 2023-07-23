from utils.mylogger import console_logger, file_logger
from datetime import datetime, timezone


def convert_to_unix_time(timestamp):
    try:
        # Parse the datetime string into a datetime object
        dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f%z")

        # Convert the datetime object to Unix time (seconds since epoch)
        unix_time = int(dt.astimezone(timezone.utc).timestamp())
    except Exception as e:
        file_logger.debug(timestamp)
        file_logger.debug(e)
        unix_time = 0

    return unix_time
