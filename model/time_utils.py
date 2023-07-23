import datetime
import time
import re


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


def get_utc_offset_in_seconds(timestamp):
    # Regex pattern to find the UTC offset at the end of the string
    pattern = r"([+-]\d{4})$"
    match = re.search(pattern, timestamp)

    if not match:
        return 0

    # Extract the sign, hours, and minutes from the match
    sign_and_offset = match.group(1)
    sign = sign_and_offset[0]
    hours = int(sign_and_offset[1:3])
    minutes = int(sign_and_offset[3:5])

    offset_seconds = ((hours * 3600) + (minutes * 60)) * (-1 if sign == "-" else 1)

    return offset_seconds


def get_timestamp_without_offset(timestamp):
    # Regex pattern to find the UTC offset at the end of the string
    pattern = r"([+-]\d{4})$"

    # Remove the UTC offset from the timestamp string
    timestamp_without_offset = re.sub(pattern, "", timestamp).strip()

    return timestamp_without_offset


def _convert_to_unix_time(timestamp):
    # Split the timestamp string on the last "-"
    unix_time = 0
    try:
        # file_logger.debug(f"raw time: {timestamp}")
        dt_string = get_timestamp_without_offset(timestamp)
        # file_logger.debug(f"without offset: {dt_string}")

        utc_offset_seconds = get_utc_offset_in_seconds(timestamp)
        # file_logger.debug(f"utc offset in seconds: {utc_offset_seconds}")

        # Parse the datetime string into a datetime object
        dt = datetime.datetime.strptime(dt_string, "%Y-%m-%dT%H:%M:%S.%f")

        utc_offset_seconds = (dt.hour * 3600) + (dt.minute * 60)

        dt = dt - datetime.timedelta(seconds=utc_offset_seconds)

        # Convert the adjusted datetime object to Unix time
        unix_time = int(time.mktime(dt.timetuple()))
    except Exception as e:
        file_logger.debug(e)
        unix_time = 0

    return unix_time
