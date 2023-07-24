# view.py
import curses
import curses.ascii

import curses.panel

import time

# import sys
from enum import auto

from .predicatedlist import PredicatedList
from view.curses_helpers.misc import ordinal_for_control_char

from utils.mylogger import file_logger

# from processqueue import ProcessQueue, ProcessTerminated
from .curses_helpers import (
    sane_screen_defaults,
    PaddedWindow,
    terminate_curses,
    resize_on_key_resize,
)

from .nclasses import HardwareLine, ExeUnitLine


from utils.mylogger import console_logger, file_logger


class View:
    """wrap an ncurses window"""

    class DisplayKind:
        LOG = auto()

    # class SignalKind:
    #     NEWLOGMSG = auto()
    """

        - NEWLOGMSG := on when a new line has been added, off when all new
            lines have been printed in _update
        - scroll_last_line := the line to which key up scrolled to last
        - /last_line_offset := offset from the last log message to
            scroll_last_line
        - last_printed_range := the last range displayed (checked to avoid
            flickering)

    """

    def __init__(self):
        self.hardware_line = HardwareLine()
        self.exeunit_line = ExeUnitLine()
        self.ESCAPED = False
        self.NEWLOGMSG = False
        self.scroll_last_line = None  # where scrolling terminates
        self.last_printed_range = None
        self.length_at_scrollback = 0
        self._displayed_window_kind = self.DisplayKind.LOG
        self._log_lines = PredicatedList()  # ordered list of log lines
        self._SUPRESS_WARN = False
        self._SUPRESS_ERROR = False
        self._SUPRESS_INFO = False
        self.resize_start_time = None

        # self._log_lines = []  # ordered list of log lines
        # self._log_lines.filterPredicate = lambda e: "ExeUnit" in e
        self._log_lines = self._log_lines  # reference to, may later reference
        #   filtered
        # self._filtered_log_lines = []  # copies of log lines filtered
        # init screen
        self._mainscreen = curses.initscr()
        sane_screen_defaults(self._mainscreen)
        self._console_scr = PaddedWindow(
            padding=(
                0,
                5,
                0,
                1,
            ),
            list_of_lines=self._log_lines,
            parentwin=self._mainscreen,
        )
        self._list_of_status_lines = [
            "",
            "",
            "",
        ]
        self._status_scr = PaddedWindow(
            padding=(0, 0, 0, self._console_scr._rowcount + 1),
            list_of_lines=self._list_of_status_lines,
            parentwin=self._mainscreen,
        )
        self._mainscreen.clear()
        self._status_scr.set_lines_to_display([None, self.exeunit_line.print()])

        # for debugging, create a logger that writes to a file
        # /init screen

    @property
    def AUTOSCROLL(self):
        return self._console_scr._AUTOSCROLL

    @AUTOSCROLL.setter
    def AUTOSCROLL(self, flagvalue):
        """set AUTOSCROLL flag

        when unset, locks a PredicatedList from refreshing as the new information is chronologically after to save cycles
        """
        self._console_scr._AUTOSCROLL = flagvalue
        if flagvalue is False:
            self._log_lines.lock()
        else:
            self._log_lines.unlock()

    @property
    def last_line_offset(self):
        # for log window, the offset from the end of the lines to print to (for ncurses helper)
        return len(self._log_lines) - self.length_at_scrollback

    def add_log_line(self, line):
        # informs view of a new log line
        self.NEWLOGMSG = True
        self._log_lines.append(line)

    def _refresh(self):
        if self._displayed_window_kind == self.DisplayKind.LOG:
            pass
        pass

    def update(self, signal=None):
        # refresh the display with optional commands from controller
        # return user interface interaction to controller
        getch = None
        getch = self._mainscreen.getch()
        if getch == curses.KEY_RESIZE:
            # check if resize has been locked (time)
            # if not, start resize timer
            resize_on_key_resize(
                self._mainscreen,
                [self._status_scr, self._console_scr],
            )

        elif getch == curses.KEY_UP:
            self._console_scr.scrollup()
        elif getch == curses.KEY_DOWN:
            self._console_scr.scrolldown()

        # check if resize timer has expired
        # if self.resize_start_time is not None:
        #     current_time = time.perf_counter()
        #     diff = current_time - self.resize_start_time
        #     if diff > self.RESIZE_DELAY:
        #         self.resize_start_time = None

        # elif getch == ordinal_for_control_char("l"):
        #     """
        #     debug
        #     10 load /home/krunch3r/lines
        #     20 reset self._log_lines
        #     """
        #     with open("/home/krunch3r/lines") as f:
        #         lines = []
        #         for line in f:
        #             if line.endswith("\n"):
        #                 lines.append(line[:-1])
        #             else:
        #                 lines.append(line)

        #         self._console_scr.set_lines_to_display(lines)
        #     pass
        elif getch == ordinal_for_control_char("w"):
            if not self._SUPRESS_WARN:
                self._SUPRESS_WARN = True
                self._log_lines.add_filter_predicate(
                    predicate_name="WARN", predicate_lambda=lambda e: "WARN" not in e
                )
            else:
                self._SUPRESS_WARN = False
                self._log_lines.del_filter_predicate(predicate_name="WARN")
            self._console_scr.redraw(reset=True)
        elif getch == ordinal_for_control_char("i"):
            if not self._SUPRESS_INFO:
                self._SUPRESS_INFO = True
                self._log_lines.add_filter_predicate(
                    predicate_name="INFO", predicate_lambda=lambda e: "INFO" not in e
                )
            else:
                self._SUPRESS_INFO = False
                self._log_lines.del_filter_predicate(predicate_name="INFO")
            self._console_scr.redraw()
        elif getch == ordinal_for_control_char("e"):
            if not self._SUPRESS_ERROR:
                self._SUPRESS_ERROR = True
                self._log_lines.add_filter_predicate(
                    predicate_name="ERROR", predicate_lambda=lambda e: "ERROR" not in e
                )
            else:
                self._SUPRESS_ERROR = False
                self._log_lines.del_filter_predicate(predicate_name="ERROR")
            self._console_scr.redraw()

        if self.NEWLOGMSG and self.AUTOSCROLL:
            if self.hardware_line.whether_print_stale():
                self._status_scr.set_lines_to_display(
                    [self.hardware_line.print(), None]
                )
            self._console_scr.redraw()
            self.NEWLOGMSG = False
        # elif self.exeunit_line.task_running:
        #     self._status_scr.set_lines_to_display([None, self.exeunit_line.print()])
        #     curses.napms(50)
        # self._status_scr.redraw()

        return None  # no interaction

    def update_resources(
        self, threads=None, memory=None, storage=None, subnet=None, init=False
    ):
        self.hardware_line.set(
            threads=threads, memory=memory, storage=storage, subnet=subnet
        )
        self._status_scr.redraw()

    def update_running_exeunit(self, start_time, resource, pid):
        if start_time is None and resource is None and pid is None:
            self.exeunit_line.reset()
        else:
            self.exeunit_line.set(start_time, resource, pid)

    def update_running_exeunit_utilization(self, duration, cpu_percentage, mem_kb):
        if self.exeunit_line.task_running:
            self.exeunit_line.set(None, None, None, duration, cpu_percentage, mem_kb)
            try:
                self._status_scr.set_lines_to_display([None, self.exeunit_line.print()])
            except TypeError:
                file_logger.debug(
                    f"TypeError printing exeunit line: duration {duration}, cpu_percentage {cpu_percentage}, mem_kib {mem_kb}"
                )
            # curses.napms(50)

    def shutdown(self):
        terminate_curses(self._mainscreen)
