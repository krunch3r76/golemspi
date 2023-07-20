# view.py
import curses
import curses.ascii

import curses.panel
import sys
from enum import Enum, auto

import time  # debug
from .predicatedlist import *

# from processqueue import ProcessQueue, ProcessTerminated
from processqueue import FileQueue
from .curses_helpers import *

from .nclasses import HardwareLine, ExeUnitLine

class View:
    """wrap an ncurses window"""

    class DisplayKind:
        LOG = auto()

    # class SignalKind:
    #     NEWLOGMSG = auto()
    """

        - NEWLOGMSG := on when a new line has been added, off when all new lines have been
                printed in _update
        - scroll_last_line := the line to which key up scrolled to last
        - /last_line_offset := offset from the last log message to scroll_last_line
        - last_printed_range := the last range displayed (checked to avoid flickering)

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
        # self._log_lines = []  # ordered list of log lines
        # self._log_lines.filterPredicate = lambda e: "ExeUnit" in e
        self._log_lines = self._log_lines  # reference to, may later reference filtered
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
        if flagvalue == False:
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
            resize_on_key_resize(
                self._mainscreen,
                [
                    self._console_scr,
                ],
            )
            self._status_scr.redraw()
            self._console_scr.redraw()
        elif getch == curses.KEY_UP:
            self._console_scr.scrollup()
        elif getch == curses.KEY_DOWN:
            self._console_scr.scrolldown()
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
        # elif getch == ordinal_for_control_char("w"):
        #     if not self._SUPRESS_WARN:
        #         self._SUPRESS_WARN = True
        #         self._log_lines.add_filter_predicate(
        #             predicate_name="WARN", predicate_lambda=lambda e: "WARN" not in e
        #         )
        #     else:
        #         self._SUPRESS_WARN = False
        #         self._log_lines.del_filter_predicate(predicate_name="WARN")
        #     self._console_scr.redraw(reset=True)
        # elif getch == ordinal_for_control_char("i"):
        #     if not self._SUPRESS_INFO:
        #         self._SUPRESS_INFO = True
        #         self._log_lines.add_filter_predicate(
        #             predicate_name="INFO", predicate_lambda=lambda e: "INFO" not in e
        #         )
        #     else:
        #         self._SUPRESS_INFO = False
        #         self._log_lines.del_filter_predicate(predicate_name="INFO")
        #     self._console_scr.redraw()
        # elif getch == ordinal_for_control_char("e"):
        #     if not self._SUPRESS_ERROR:
        #         self._SUPRESS_ERROR = True
        #         self._log_lines.add_filter_predicate(
        #             predicate_name="ERROR", predicate_lambda=lambda e: "ERROR" not in e
        #         )
        #     else:
        #         self._SUPRESS_ERROR = False
        #         self._log_lines.del_filter_predicate(predicate_name="ERROR")
        #     self._console_scr.redraw()

        if self.NEWLOGMSG and self.AUTOSCROLL:
            if self.hardware_line.whether_print_stale():
                self._status_scr.set_lines_to_display([self.hardware_line.print(), None])
            self._console_scr.redraw()
            self.NEWLOGMSG = False
        if self.exeunit_line.task_running:
            self._status_scr.set_lines_to_display([None, self.exeunit_line.print()], redraw=False)
            # self._status_scr.redraw()

        return None  # no interaction

    def update_resources(
        self, threads=None, memory=None, storage=None, subnet=None, init=False
    ):
        self.hardware_line.set(
            threads=threads, memory=memory, storage=storage, subnet=subnet
        )
        self._status_scr.redraw()

    def update_running_exeunit( self, start_time, resource, pid ):
        if start_time is None and resource is None and pid is None:
            self.exeunit_line.reset()
        else:
            self.exeunit_line.set(start_time, resource, pid)

    def shutdown(self):
        terminate_curses(self._mainscreen)
