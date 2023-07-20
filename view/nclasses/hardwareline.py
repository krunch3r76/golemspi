# hardwareline.py
# implements HardwareLine object for printing to ncurses

import datetime
from decimal import Decimal
from typing import TypeVar
import time

class TimestampedValue:
    def __init__(self, value):
        self._value = value
        self.timestamp: datetime.datetime = None

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self._value = new_value
        if new_value is not None:
            self.timestamp = datetime.datetime.now().timestamp()
        else:
            self.timestamp = None

    # def __format__(self, format_spec: str) -> str:
    #     return format(self._value, format_spec)

    # def __str__(self):
    #     return str(self._value)

    # def __repr__(self):
    #     return f"TimestampedValue(value={self._value}, timestamp={self.timestamp})"


class HardwareLine:
    """
    Represents an ncurses line with subnet, threads, memory and storage.

    As __str__, takes the form of:
    subnet: public                threads: 31.0                 memory (GiB): 42.75           storage (GiB): 331.07
    """

    def __init__(self, subnet=None, threads=None, memory=None, storage=None):
        """
        Initialize a new HardwareLine instance with optional subnet, threads, memory and storage values

        Args:
            subnet (str or None): The subnet value
            threads (int or None):  The threads value
            memory (float or None): the memory value
            storage (float or None): the storage value

        Notes:
            The 'timestamp' attribute is a dictionary that maps attribute names to the timestamps
            of when they were last set."""
        self._subnet = (
            TimestampedValue(str(subnet))
            if subnet is not None
            else TimestampedValue(None)
        )
        self._threads = (
            TimestampedValue(int(threads))
            if threads is not None
            else TimestampedValue(None)
        )
        self._memory = (
            TimestampedValue(float(memory))
            if memory is not None
            else TimestampedValue(None)
        )
        self._storage = (
            TimestampedValue(float(storage))
            if storage is not None
            else TimestampedValue(None)
        )
        self._last_print_timestamp = datetime.datetime.now().timestamp() - 1
        self._last_set_timestamp = datetime.datetime.now().timestamp()

    @property
    def subnet(self):
        return self._subnet.value

    @subnet.setter
    def subnet(self, value):
        self._subnet.value = value

    @property
    def threads(self):
        return self._threads.value

    @threads.setter
    def threads(self, value):
        self._threads.value = value

    @property
    def memory(self):
        return self._memory.value

    @memory.setter
    def memory(self, value):
        self._memory.value = value

    @property
    def storage(self):
        return self._storage.value

    @storage.setter
    def storage(self, value):
        self._storage.value = value

    def print(self):
        subnet = f"subnet: {self.subnet}" if self.subnet is not None else "subnet: ?"

        threads = (
            f"threads: {self.threads}" if self.threads is not None else "threads: ?"
        )

        memory = (
            f"memory (GiB): {self.memory:.2f}"
            if self.memory is not None
            else "memory (GiB): ?"
        )

        storage = (
            f"storage (GiB): {self.storage:2f}"
            if self.storage is not None
            else "storage (GiB): ?"
        )
        self._last_print_timestamp = datetime.datetime.now().timestamp()

        return f"{subnet:<25}    {threads:<25}    {memory:<25}    {storage:<25}"

    def whether_print_stale(self):
        return self._last_set_timestamp > self._last_print_timestamp

    def set(self, threads=None, memory=None, storage=None, subnet=None):
        """update attributes provided or ignore"""
        if threads is not None:
            self.threads = threads
        if memory is not None:
            self.memory = memory
        if storage is not None:
            self.storage = storage
        if subnet is not None:
            self.subnet = subnet
        self._last_set_timestamp = datetime.datetime.now().timestamp()

class ExeUnitLine:
    """
    Represents a line for ncurses with task url, pid, and time running

    As __str__, takes the form of:
    task url: ?     pid: ?      time_running: ?
    """

    def __init__(self):
        """
        Initialize a new HardwareLine instance showing no task running
        """
        self.task_running = False
        self._time_start = None
        self._task_url = None
        self._pid = None

    def _get_elapsed_time(self, start_time, current_time):
        elapsed_seconds = current_time - start_time
        hours = int(elapsed_seconds // 3600)
        minutes = int((elapsed_seconds % 3600) // 60)
        seconds = int(elapsed_seconds % 60)

        if hours > 0:
            return f"{hours}h {minutes} min {seconds}sec"
        elif minutes > 0:
            return f"{minutes} min {seconds} sec"
        else:
            return f"{seconds} sec"

    def print(self):
        if not self.task_running:
            return f"NO TASK RUNNING CURRENTLY"
        else:
            # calculate time elasped since start time
            elapsed_time = self._get_elapsed_time(self._time_start, time.time())
            return f"resource: {self._task_url:<26}\tpid: {self._pid:<26}\ttime_running: {elapsed_time:<26}"

    def set(self, time_start, task_url, pid):
        self._time_start = time_start
        if task_url is not None: 
            self._task_url = task_url
        else:
            task_url = "unknown"
        self._pid = pid
        self.task_running = True

    def reset(self):
        self.task_running = False
        self._time_start = None
        self._task_url = None
        self._pid = None

