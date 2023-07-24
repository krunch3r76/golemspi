# view/curses_helpers/paddedwindow.py
import curses
import textwrap
from .get_printable_range import get_printable_range

from utils.mylogger import console_logger, file_logger


class PaddedWindow:
    """a scrollable window set up with margins

    wraps an ncurses window
    + scrollup()
    + scrollwdown()
    + redraw()
    + resize()
    + redrawwin()
    + clear()
    + move()
    + addstr()

    / padding
    / rowcount
    / colcount
    """

    def __init__(self, padding, list_of_lines=None, parentwin=None):
        """create a scrollable subwindow or new window with the specified absolute padding


        Args:
            padding: a tuple of margins in the directions n, w, e, s
            list_of_lines: the sequence of lines referenced for displaying
            [parentwin]: the window to which this shall be a subwindow
        """

        def _create_window(padding):
            # padding is a tuple (w0, n1, e2, s3)
            if parentwin is None:
                raise Exception("untested without a parent screen/window")
            else:
                W, N, E, S = range(4)
                # win = parentwin.subwin(
                win = parentwin.subwin(
                    curses.LINES - padding[N] - padding[S],  # height
                    curses.COLS - padding[W] - padding[E],  # width
                    padding[N],  # y
                    padding[W],  # x
                )
            return win

        if list_of_lines is None:
            list_of_lines = ["", ""]
        self._win = _create_window(padding)
        self._win.scrollok(True)
        self._padding = padding
        self._lines = list_of_lines
        self._AUTOSCROLL = True  # state of scrolling
        self.__length_at_scrollback = len(self._lines)  # length cutoff for scrollback
        self._pad = None
        # self._last_printed_range = None  # useful for when resizing to expand down

    @property
    def _length_at_scrollback(self):
        return self.__length_at_scrollback

    @_length_at_scrollback.setter
    def _length_at_scrollback(self, newval):
        if newval > len(self._lines):
            raise Exception("Cannot scroll beyond array length")
        elif newval < 0:
            raise Exception("Length at scrollback cannot be negative")

        self.__length_at_scrollback = newval

    def set_lines_to_display(self, new_lines_to_display, middle_line=None, redraw=True):
        """
        replace the buffer of lines displayed and redisplay
        Args:
            new_lines_to_display: a reference to lines to display
            [middle_line]: the line the display should center on (TODO)
        """
        for index, line in enumerate(new_lines_to_display):
            if line is not None:
                self._lines[index] = line

        if middle_line is None:
            self._length_at_scrollback = len(self._lines)
            self._AUTOSCROLL = True

        if redraw:
            self.redraw()
        else:
            self.refresh()
            # self._win.refresh()

    @property
    def _printable_range(self):
        # computed property yielding the range of lines printable given the end scrollback offset
        if self._AUTOSCROLL or self._length_at_scrollback <= 0:
            last_line_offset = None
        else:
            last_line_offset = self._length_at_scrollback - 1

        return get_printable_range(
            lines=self._lines,
            last_line_offset=last_line_offset,
            countRows=self._rowcount,
            countCols=self._colcount,
        )

    def scrollup(self, lines_to_scroll=1):
        """scrollup |lines_to_scroll| count and redraw

        Args:
            lines_to_scroll: count number of lines to scroll up (not implemented)
        """

        # scroll a line up if possible

        # test if first line is displayed
        if self._printable_range is not None and self._printable_range[0] == 0:
            return
        self._AUTOSCROLL = False
        self._length_at_scrollback = self._length_at_scrollback - 1
        if self._length_at_scrollback < 1:
            self._length_at_scrollback = 0

        self.redraw()

    def scrolldown(self, lines_to_scroll=1):
        """scrolldown |lines_to_scroll| count and redraw

        Args:
            lines_to_scroll:  number of lines to scroll down (not implemented)
        """
        if self._AUTOSCROLL:
            return

        self._length_at_scrollback = self._length_at_scrollback + 1

        if self._length_at_scrollback == len(self._lines):
            self._AUTOSCROLL = True

        self.redraw()

    def redraw(self, reset=False):
        """print lines in the printable_range to log console (main screen) and refresh"""

        W, N, E, S = range(4)
        if self._AUTOSCROLL or reset:
            # update offset at which scrolling would resume
            self._length_at_scrollback = len(self._lines)

        printable_range = self._printable_range
        # file_logger.debug(f"{printable_range}")
        if printable_range[1] - printable_range[0] < 1:
            printable_range = None

        if printable_range is not None:
            # Get dimensions of the window
            (h, w) = self._win.getmaxyx()

            # Create a new pad if it doesn't exist or if the window has been resized
            if self._pad is None or self._pad.getmaxyx() != (h, w):
                # self._pad = curses.newpad(h + 1, w + 0)
                self._pad = curses.newpad(h + 0, w + 0)
            else:
                # Clear the pad before adding new content
                self._pad.clear()
            # self._pad = curses.newpad(h + 0, w + 0)

            row_offset = 0
            for line_offset in range(printable_range[0], printable_range[1] + 1):
                wrapped_lines = textwrap.wrap(self._lines[line_offset], w)
                for wrapped_line in wrapped_lines:
                    self._pad.insstr(row_offset, 0, wrapped_line)
                    row_offset += 1
            curses.napms(15)
            # Copy the pad to the window
            self._pad.refresh(
                0,
                0,
                self._padding[N],
                self._padding[W],
                h - 1 + self._padding[N],
                w - 1 + self._padding[W],
            )

            # Update the physical screen with the changes made to the pad
            # curses.doupdate()

    # def redraw_(self, reset=False):
    #     """print lines in the printable_range to log console (main screen) and refresh"""

    #     if self._AUTOSCROLL or reset:
    #         # update offset at which scrolling would resume
    #         self._length_at_scrollback = len(self._lines)

    #     printable_range = self._printable_range
    #     if printable_range is not None:
    #         # Get dimensions of the window
    #         (h, w) = self._win.getmaxyx()

    #         # Create a new pad with the same dimensions
    #         pad = curses.newpad(h + 1, w)

    #         row_offset = 0
    #         for line_offset in range(printable_range[0], printable_range[1] + 1):
    #             wrapped_lines = textwrap.wrap(self._lines[line_offset], w)
    #             for wrapped_line in wrapped_lines:
    #                 pad.addstr(row_offset, 0, wrapped_line)
    #                 row_offset += 1

    #         # Copy the pad to the window
    #         W, N, E, S = range(4)
    #         pad.refresh(
    #             0,
    #             0,
    #             self._padding[N],
    #             self._padding[W],
    #             h - 1 + self._padding[N],
    #             w - 1 + self._padding[W],
    #         )

    #         # Now refresh the window
    #         self._win.overwrite(pad)
    #         self._win.refresh()
    #         if len(self._lines) < 10:
    #             file_logger.debug(self._lines)

    def resize_fit(self):
        """fit window to current dimensions"""
        # curses.update_lines_cols()  # redundant?
        W, N, E, S = range(4)
        try:
            self._win.resize(
                curses.LINES - self._padding[N] - self._padding[S],
                curses.COLS - self._padding[W] - self._padding[E],
            )
            if self._pad is not None:
                self._pad.clear()
        except Exception as e:
            file_logger.debug("resize error {e}", e)

    def redrawwin(self):
        """wrap redrawwin
        * redrawwin() touches the entire window, causing it to be completely redrawn on
        the next refresh() call"""
        self._win.redrawwin()

    def refresh(self, *args, **kwargs):
        """wrap refresh
        * update the display immediately (sync actual screen with previous drawing/deleting
        methods
        """
        self._win.refresh()
        # self._win.noutrefresh()
        # curses.doupdate()

    def getmaxyx(self):
        # wrap getmaxyx
        return self._win.getmaxyx()

    def clear(self):
        """wrap clear()

        * Like erase(), but also causes the whole window to be repainted upon next call
        to refresh()

        notes: it should be sufficient to simply erase and let redrawwin inform refresh()
        """
        self._win.clear()

    # def addstr(self, *args, **kwargs):
    #     self._win.addstr(*args, **kwargs)

    @property
    def _rowcount(self):
        # maxy
        y, _ = self._win.getmaxyx()
        return y

    @property
    def _colcount(self):
        # maxx
        _, x = self._win.getmaxyx()
        return x

    @property
    def padding(self):
        # return padding sequence
        return self._padding

    @padding.setter
    def padding(self, padding_tuple):
        # update padding given the tuple
        raise Exception("setting padding publicly not supported")
