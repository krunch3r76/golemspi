# events/event.py
import pprint


class Event:
    def __init__(self, timestamp):
        self.timestamp = timestamp  # in the minimum we expect an log message event to parse a timestamp

    # def __repr__(self):
    #     attributes = self._get_attributes()
    #     return f"{type(self).__name__}({attributes})"

    def asdict(self):
        return self._get_attributes()

    def _get_attributes(self):
        return {
            attr: getattr(self, attr)
            for attr in self.__dict__
            if not attr.startswith("__")
        }
