# File: golemspi/view/ncurses_window.py
import curses
import textwrap
from .utils.predicatedlist import PredicatedList

from utils.mylogger import console_logger, file_logger


class _NcursesWindow:
    def __init__(self, margin_top, margin_left, margin_bottom, margin_right):
        self._margin_top = margin_top
        self._margin_left = margin_left
        self._margin_bottom = margin_bottom
        self._margin_right = margin_right

        # Get the total number of lines and columns
        total_lines, total_cols = curses.LINES, curses.COLS

        # Compute the window size based on the margins
        self._win_height = total_lines - margin_top - margin_bottom
        self._win_width = total_cols - margin_left - margin_right

        # Create the window with the computed size
        self._window = curses.newwin(
            self._win_height, self._win_width, margin_top, margin_left
        )


class NscrollingWindow(_NcursesWindow):
    def __init__(self, margin_top, margin_left, margin_bottom, margin_right):
        super().__init__(margin_top, margin_left, margin_bottom, margin_right)

        self._window.scrollok(True)

        self._lines = PredicatedList()
        self._last_line_index = -1  # Track the index of the last displayed line
        self._num_lines_on_screen = 0
        self.autoscroll = True
        self._needs_redraw = False
        self._row_of_last_line_displayed = -1
        self._index_to_first_line_displayed = None

    # def _count_wrapped_lines(self, line):
    #     return len(textwrap.wrap(line, self._win_width))

    def add_line(self, line):
        self._lines.append(line)
        # if self.autoscroll:
        #     self._last_line_index += 1
        #     self._needs_redraw = True

    def _blank_rowcount(self):
        return self._win_height - 1 - self._row_of_last_line_displayed

    def _find_rows_printable_up_to_last(self, negative_offset=0):
        rows_available_to_write_to = self._win_height
        line_cursor_bottom = self._last_line_index - negative_offset
        line_cursor = line_cursor_bottom
        buffer = []
        while line_cursor >= 0:  # do not try to read lines beyond the first in buffer
            next_wrapped_line = textwrap.wrap(self._lines[line_cursor], self._win_width)
            count_lines_needed = len(next_wrapped_line)
            if count_lines_needed <= rows_available_to_write_to:
                buffer.append(next_wrapped_line)
                rows_available_to_write_to -= count_lines_needed
            else:
                break
            line_cursor -= 1
        buffer.reverse()
        self._row_of_last_line_displayed = self._win_height - 1
        # flatten buffer
        wrapped_visible_lines = [line for sublist in buffer for line in sublist]
        return wrapped_visible_lines, (
            line_cursor + 1,
            line_cursor_bottom,
        )

    def refresh_view(self, clear=False):
        if len(self._lines) == 0:
            return

        # def rows_occupied_by_up_to_last_line():

        if self.autoscroll:

            def rows_available_to_write():
                return self._win_height - 1 - self._row_of_last_line_displayed

            def count_lines_unwritten():
                return len(self._lines) - 1 - self._last_line_index

            while rows_available_to_write() > 0 and count_lines_unwritten() > 0:
                next_line_index = self._last_line_index + 1
                next_line = self._lines[next_line_index]
                if next_line != "":
                    next_line_wrapped = textwrap.wrap(next_line, self._win_width)
                else:
                    next_line_wrapped = [""]
                rows_needed_for_writing = len(next_line_wrapped)
                row_cursor = self._row_of_last_line_displayed + 1

                if rows_available_to_write() < rows_needed_for_writing:
                    # scroll lines
                    lines_to_scroll = rows_needed_for_writing - rows_available_to_write
                    self._window.scroll(lines_to_scroll)
                    row_cursor -= lines_to_scroll

                # write lines to available space
                for line in next_line_wrapped:
                    self._window.move(row_cursor, 0)
                    # self._window.clrtoeol()
                    self._window.insstr(row_cursor, 0, line)
                    row_cursor += 1
                self._row_of_last_line_displayed = row_cursor - 1
                self._last_line_index = next_line_index

            while count_lines_unwritten() > 0:
                next_line_index = self._last_line_index + 1
                next_line = self._lines[next_line_index]
                next_line_wrapped = textwrap.wrap(next_line, self._win_width)
                rows_needed_for_writing = len(next_line_wrapped)
                self._window.scroll(rows_needed_for_writing)
                row_cursor = self._win_height - rows_needed_for_writing
                for line in next_line_wrapped:
                    self._window.move(row_cursor, 0)
                    # self._window.clrtoeol()
                    self._window.insstr(row_cursor, 0, line)
                    row_cursor += 1
                    self._last_line_index = next_line_index

        elif clear:
            self._window.clear()

            rows_printable_up_to_last, _ = self._find_rows_printable_up_to_last()
            for i, row in enumerate(rows_printable_up_to_last):
                self._window.insstr(i, 0, row)

        self._window.refresh()

    def scroll_up(self, n=1):
        for _ in range(n):
            _, (
                index_corresponding_to_first_line,
                _,
            ) = self._find_rows_printable_up_to_last()

            if index_corresponding_to_first_line == 0:
                break
            if self._last_line_index - 1 >= 0 and self._blank_rowcount() == 0:
                self.autoscroll = False
                self._last_line_index -= 1
            self.refresh_view(clear=True)

    def scroll_down(self, n=1):
        for _ in range(n):
            if (
                self._last_line_index + 1 < len(self._lines)
                and self._blank_rowcount() == 0
            ):
                self._last_line_index += 1
                if self._last_line_index == len(self._lines) - 1:
                    self.autoscroll = True
                    break
        self.refresh_view(clear=True)

    def resize(self):
        maxy, maxx = curses.LINES - 1, curses.COLS - 1
        self._win_width = maxx - self._margin_left - self._margin_right
        self._win_height = maxy - self._margin_top - self._margin_bottom
        self._window.resize(self._win_height, self._win_width)


# class NcursesWindowPad:
#     def __init__(
#         self, nlines, ncols, margin_top, margin_left, margin_bottom, margin_right, scr
#     ):
#         # Create pad larger than the screen size to store lines outside of the visible area.
#         # Adjust the size based on your needs
#         self.pad = curses.newpad(1000, ncols)
#         self._margin_top = margin_top
#         self._margin_left = margin_left
#         self._margin_bottom = margin_bottom
#         self._margin_right = margin_right
#         self.scr = scr
#         self.lines = []
#         self._win_width = ncols
#         self._win_height = nlines

#     def add_line(self, line):
#         """
#         Add a line to the pad and scroll as needed.
#         """
#         self.lines.append(line)
#         maxy, maxx = self.scr.getmaxyx()
#         max_lines = maxy - self._margin_top - self._margin_bottom
#         start = max(0, len(self.lines) - max_lines)
#         self.pad.addstr(len(self.lines) - 1, 0, line)
#         self.pad.refresh(
#             start,
#             0,
#             self._margin_top,
#             self._margin_left,
#             maxy - self._margin_bottom,
#             maxx - self._margin_right,
#         )
