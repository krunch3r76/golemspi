# view.py
import curses
import curses.ascii

import curses.panel
import sys
from enum import Enum, auto
import asyncio

# from processqueue import ProcessQueue, ProcessTerminated
from processqueue import FileQueue
from .curses_helpers import *


class View:
    class DisplayKind:
        LOG = auto()

    def __init__(self, queue_in: asyncio.Queue):
        self._queue_in = queue_in
        self._displayed_window_kind = self.DisplayKind.LOG
        self._log_lines = []  # ordered list of log lines
        self._filtered_log_lines = []  # copies of log lines filtered
        self._bottom_offset = None  # last log line to display

    def add_log_line(self, line):
        # informs view of a new log line
        self._log_lines.append(line)
        self._refresh()

    def _refresh(self):
        if self._displayed_window_kind == self.DisplayKind.LOG:
            self._screen.clear()
            # clear window
            # reference window dimensions (columncount, rowcount)
            # calculate space occupied by viewable lines
            pass
        pass

    def update(self, signal=None):
        # refresh the display with optional commands from controller
        # return user interface interaction to controller

        printable_range = get_printable_range(
            self._log_lines, self._bottom_offset, win=self._screen
        )
        countRows, countColumns = self._screen.getmaxyx()
        if printable_range is not None:
            self._screen.move(0, 0)
            for offset in range(printable_range[0], printable_range[1]):
                self._screen.addstr(
                    self._log_lines[offset]
                    + f": {countRows},{countColumns},{printable_range}"
                    + "\n"
                )

            self._screen.addstr(
                self._log_lines[printable_range[1]]
                + f": {countRows},{countColumns},{printable_range}"
            )
            # self._screen.addstr(self._log_lines[printable_range[1]])

        self._screen.refresh()
        return None  # no interaction

    def shutdown(self):
        terminate_curses(self._screen)

    async def __call__(self):
        # tasked
        # init screen
        self._screen = curses.initscr()
        sane_screen_defaults(self._screen)
        self._screen.clear()
        # /init screen
        while True:
            try:
                signal = self._queue_in.get_nowait()
            except asyncio.queues.QueueEmpty:
                self._screen.addstr("empty")
                await asyncio.sleep(0.001)
            else:
                self.add_log_line(signal)
                self.update()
