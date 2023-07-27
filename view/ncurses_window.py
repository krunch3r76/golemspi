# File: golemspi/view/ncurses_window.py
import curses
import textwrap
from .utils.predicatedlist import PredicatedList

from utils.mylogger import console_logger, file_logger


class _NcursesWindow:
    def __init__(
        self, nlines, ncols, margin_top, margin_left, margin_bottom, margin_right
    ):
        self._margin_top = margin_top
        self._margin_left = margin_left
        self._margin_bottom = margin_bottom
        self._margin_right = margin_right
        self._win_width = ncols
        self._win_height = nlines

        self._window = curses.newwin(nlines, ncols, margin_top, margin_left)


class NcursesWindow(_NcursesWindow):
    def __init__(
        self, nlines, ncols, margin_top, margin_left, margin_bottom, margin_right
    ):
        super().__init__(
            nlines, ncols, margin_top, margin_left, margin_bottom, margin_right
        )
        self._window = curses.newwin(nlines, ncols, margin_top, margin_left)
        self._window.scrollok(True)

        self._lines = PredicatedList()  # Your custom list type
        self._last_line_index = -1  # Track the index of the last displayed line
        self._num_lines_on_screen = 0
        self.autoscroll = True
        self._needs_redraw = False
        self._row_of_last_line_displayed = -1

    def count_wrapped_lines(self, line):
        return len(textwrap.wrap(line, self._win_width))

    def add_line(self, line):
        self._lines.append(line)
        # if self.autoscroll:
        #     self._last_line_index += 1
        #     self._needs_redraw = True

    def _blank_rowcount(self):
        return self._win_height - 1 - self._row_of_last_line_displayed

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
                next_line_wrapped = textwrap.wrap(next_line, self._win_width)
                rows_needed_for_writing = len(next_line_wrapped)
                row_cursor = self._row_of_last_line_displayed + 1
                if rows_available_to_write() < rows_needed_for_writing:
                    lines_to_scroll = rows_needed_for_writing - rows_available_to_write
                    self._window.scroll(lines_to_scroll)
                    row_cursor -= lines_to_scroll
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
                self._window.refresh()

        elif clear:
            self._window.clear()

            def find_rows_printable_up_to_last():
                rows_available_to_write_to = self._win_height
                # rows_occupied_by_wrapped_lines = 0
                cursor = self._last_line_index
                buffer = []
                while (
                    cursor >= 0
                ):  # do not try to read lines beyond the first in buffer
                    next_wrapped_line = textwrap.wrap(
                        self._lines[cursor], self._win_width
                    )
                    cursor -= 1
                    count_lines_needed = len(next_wrapped_line)
                    if count_lines_needed <= rows_available_to_write_to:
                        buffer.append(next_wrapped_line)
                        rows_available_to_write_to -= count_lines_needed
                    else:
                        break
                # flatten buffer
                buffer.reverse()
                self._row_of_last_line_displayed = self._win_height - 1
                wrapped_visible_lines = [line for sublist in buffer for line in sublist]
                return wrapped_visible_lines

            rows_printable_up_to_last = find_rows_printable_up_to_last()
            for i, row in enumerate(rows_printable_up_to_last):
                self._window.insstr(i, 0, row)

            # how many rows fit from the _last_line_index

            # rows_available_to_write_to = self._win_height - 1
            # rows_occupied_by_wrapped_lines = 0
            # cursor = self._last_line_index
            # buffer = []
            # while cursor >= 0:  # do not try to read lines beyond the first in buffer
            #     next_wrapped_line = textwrap.wrap(self._lines[cursor], self._win_width)
            #     cursor=-1
            #     count_lines_needed = len(next_wrapped_line)
            #     if count_lines_needed <= rows_available_to_write_to:
            #         buffer.append(next_wrapped_line)
            #         rows_available_to_write_to -= count_lines_needed
            #     else:
            #         break
            # # flatten buffer
            # wrapped_visible_lines = [
            #     line for sublist in buffer for line in sublist
            # ]  # Flatten the list

            self._window.refresh()

    def scroll_up(self, n=1):
        if self._last_line_index - n >= 0 and self._blank_rowcount() == 0:
            self.autoscroll = False
            self._last_line_index -= n
            self.refresh_view(clear=True)
        else:
            file_logger.debug(
                f"scroll up failed, last_line_index: {self._last_line_index} and blank rowcount: {self._blank_rowcount()}"
            )

    def scroll_down(self, n=1):
        if self._last_line_index + n < len(self._lines) and self._blank_rowcount() == 0:
            self._last_line_index += n
            self.refresh_view(clear=True)
            if self._last_line_index == len(self._lines) - 1:
                self.autoscroll = True

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
