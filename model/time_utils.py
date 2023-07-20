import datetime
import time


def convert_to_unix_time(timestamp):
    # Split the timestamp string on the last "-"
    unix_time = 0
    try:
        split_index = timestamp.rindex("-")
        dt_string = timestamp[:split_index]
        utc_offset_string = timestamp[split_index + 1 :]

        # Parse the datetime string into a datetime object
        dt = datetime.datetime.strptime(dt_string, "%Y-%m-%dT%H:%M:%S.%f")

        # Check if UTC offset is present in the timestamp string
        if utc_offset_string:
            # Convert the UTC offset string to seconds
            hours = int(utc_offset_string[:2])
            minutes = int(utc_offset_string[2:])

            offset_seconds = (hours * 3600) + (minutes * 60)
            utc_offset_seconds = int(utc_offset_string) / 100 * 60 * 60

            # Adjust the datetime object based on the UTC offset
            if utc_offset_seconds >= 0:
                dt = dt - datetime.timedelta(seconds=utc_offset_seconds)
            else:
                dt = dt + datetime.timedelta(seconds=abs(utc_offset_seconds))

        # Convert the adjusted datetime object to Unix time
        unix_time = int(time.mktime(dt.timetuple()))
    except:
        unix_time = 0

    return unix_time
