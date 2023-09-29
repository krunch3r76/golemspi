from .ncurses_window import _NcursesWindow

import curses
import textwrap

from utils.mylogger import file_logger


class NcursesWindowScrolling(_NcursesWindow):
    def __init__(
        self,
        margin_top,
        margin_left,
        margin_bottom,
        margin_right,
        line_buffer_class=None,
    ):
        super().__init__(margin_top, margin_left, margin_bottom, margin_right)
        self.__row_of_last_line_displayed = -1
        NcursesWindowScrolling.reconstruct(self)

        if line_buffer_class is None:
            self._lines = list()
        else:
            self._lines = line_buffer_class()

        self._index_to_last_line_displayed = (
            -1
        )  # Track the index of the last displayed line
        self._index_to_first_line_displayed = -1
        self.autoscroll = True

    @property
    def _row_of_last_line_displayed(self):
        return self.__row_of_last_line_displayed

    @_row_of_last_line_displayed.setter
    def _row_of_last_line_displayed(self, value):
        self.__row_of_last_line_displayed = value

    def _write_wrapped_lines(self, row_cursor, next_line_wrapped):
        """write a line at the row cursor and advance the row cursor

        notes: override in subclass for special formatting
        """
        for i, line in enumerate(next_line_wrapped):
            self._window.move(row_cursor, 0)
            self.insstr_truncated(row_cursor, 0, line)
            self._row_of_last_line_displayed = row_cursor
            row_cursor += 1
        return row_cursor - 1

    def reconstruct(self):
        """call the super reconstruct but post-process for scrolling"""
        super().reconstruct()
        self._window.scrollok(True)

    def scroll_to_bottom(self):
        self.autoscroll = True
        _, (
            index_corresponding_to_first_line,
            index_corresponding_to_last_line,
        ) = self._find_rows_printable_up_to_last(len(self._lines) - 1)

        self.refresh_view(
            index_to_first=index_corresponding_to_first_line,
            index_to_last=index_corresponding_to_last_line,
        )

    def _blank_rowcount(self):
        """return the number of rows unfilled beneath the last row written to"""
        return self._win_height - 1 - self._row_of_last_line_displayed

    def scroll_to_top(self):
        self.autoscroll = False
        _, (
            index_corresponding_to_first_line,
            index_corresponding_to_last_line,
        ) = self._find_rows_printable_from_top()

        self.refresh_view(
            index_to_first=index_corresponding_to_first_line,
            index_to_last=index_corresponding_to_last_line,
        )

    def scroll_up(self, n=1):
        if self._index_to_first_line_displayed == 0:
            return

        change = False
        index_corresponding_to_first_line = None
        index_corresponding_to_last_line = None

        for _ in range(n):
            # scroll up n lines

            # calculate indices that fit in the window
            previous_index_to_last_line_displayed = (
                self._index_to_last_line_displayed - 1
            )
            _, (
                index_corresponding_to_first_line,
                index_corresponding_to_last_line,
            ) = self._find_rows_printable_up_to_last(
                previous_index_to_last_line_displayed
            )

            # update state
            self._index_to_last_line_displayed -= 1

            if (
                previous_index_to_last_line_displayed >= 0
                and self._blank_rowcount() == 0
            ):
                self.autoscroll = False
                change = True

            if index_corresponding_to_first_line == 0:
                break

        curses.napms(3)
        if change or index_corresponding_to_first_line == 0:
            self.refresh_view(
                index_to_first=index_corresponding_to_first_line,
                index_to_last=index_corresponding_to_last_line,
            )

    def scroll_down(self, n=1):
        index_corresponding_to_first_line = None
        index_corresponding_to_last_line = None

        next_index_to_last_line_displayed = self._index_to_last_line_displayed + 1

        # or test for autoscroll
        if self._index_to_last_line_displayed == len(self._lines) - 1:
            return

        for _ in range(n):
            _, (
                index_corresponding_to_first_line,
                index_corresponding_to_last_line,
            ) = self._find_rows_printable_up_to_last(next_index_to_last_line_displayed)

            next_index_to_last_line_displayed += 1
            if next_index_to_last_line_displayed > len(self._lines) - 1:
                break

        self.refresh_view(
            index_to_first=index_corresponding_to_first_line,
            index_to_last=index_corresponding_to_last_line,
        )

        if self._index_to_last_line_displayed == len(self._lines) - 1:
            self.autoscroll = True
        curses.napms(3)

    def _rows_available_to_write(self):
        if self._row_of_last_line_displayed == -1:
            return self._win_height

        return self._win_height - self._row_of_last_line_displayed - 1

    def _write_next_line_as_wrapped(self, next_line, wrapper=None):
        # write lines after self._row_of_last_line_displayed scrolling as needed
        if wrapper is None:
            wrapper = textwrap.wrap

        virtual_win_width = self._win_width
        next_line_wrapped = (
            wrapper(next_line, virtual_win_width) if next_line != "" else [""]
        )

        rows_needed_for_writing = len(next_line_wrapped)

        if rows_needed_for_writing > self._rows_available_to_write():
            # scroll as many lines as would be needed to write the next wrapped line
            lines_to_scroll = rows_needed_for_writing - self._rows_available_to_write()
            self._window.scroll(lines_to_scroll)
            row_cursor = self._win_height - 0 - lines_to_scroll
            row_cursor = self._write_wrapped_lines(row_cursor, next_line_wrapped)
            self._row_of_last_line_displayed = row_cursor
        else:
            row_cursor = self._row_of_last_line_displayed + 1
            if row_cursor < 0:
                row_cursor = 0
            row_cursor = self._write_wrapped_lines(row_cursor, next_line_wrapped)
            self._row_of_last_line_displayed = row_cursor

        # advance reference to index to last line displayed by 1
        self._index_to_last_line_displayed += 1

    def _find_rows_printable_up_to_last(self, last_index, fnc_line_min_length=None):
        rows_available_to_write_to = self._win_height
        line_cursor_bottom = last_index
        line_cursor = line_cursor_bottom
        buffer = []

        while line_cursor >= 0:  # do not try to read lines beyond the first in buffer
            next_line = self._lines[line_cursor]

            if fnc_line_min_length is None:
                adjusted_win_length = self._win_width
            else:
                adjusted_win_length = fnc_line_min_length(next_line)

            next_wrapped_line = textwrap.wrap(next_line, adjusted_win_length)
            count_lines_needed = len(next_wrapped_line)
            if count_lines_needed <= rows_available_to_write_to:
                buffer.append(next_wrapped_line)
                rows_available_to_write_to -= count_lines_needed
            else:
                break

            line_cursor -= 1
        buffer.reverse()
        line_cursor += 1

        # flatten buffer
        wrapped_visible_lines = [line for sublist in buffer for line in sublist]
        return wrapped_visible_lines, (
            line_cursor,
            line_cursor_bottom,
        )

    def _find_rows_printable_from_top(self, top_index=0, fnc_line_min_length=None):
        """Return lines from the top and inclusive range from the buffer that, when wrapped, would fill the available space."""
        rows_available_to_write_to = self._win_height
        line_cursor_top = 0
        line_cursor = line_cursor_top

        buffer = []
        while (
            line_cursor <= self._win_height - 1
            and top_index + line_cursor <= len(self._lines) - 1
        ):
            next_line = self._lines[top_index + line_cursor]

            if fnc_line_min_length is not None:
                adjusted_win_length = self._win_width
            else:
                adjusted_win_length = self.fnc_line_min_length(next_line)
            next_wrapped_line = textwrap.wrap(next_line, adjusted_win_length)
            count_lines_needed = len(next_wrapped_line)
            if count_lines_needed <= rows_available_to_write_to:
                buffer.append(next_wrapped_line)
                rows_available_to_write_to -= count_lines_needed
                line_cursor += 1
            else:
                break
        wrapped_visible_lines = [line for sublist in buffer for line in sublist]
        bottom_index = top_index + line_cursor - 1
        return wrapped_visible_lines, (top_index, bottom_index)

    def add_line(self, line):
        """Add a line to the internal buffer


        Notes:
            refresh_view must be called externally to reflect any changes
        """
        self._lines.append(line)

    def refresh_view(self, index_to_first=None, index_to_last=None, wrapper=None):
        def _refresh_view(index_to_first, index_to_last, wrapper):
            if self._resizing:
                self._row_of_last_line_displayed = -1
                self._index_to_last_line_displayed = index_to_first - 1

            if self.autoscroll:
                while self._index_to_last_line_displayed < len(self._lines) - 1:
                    next_line_index = self._index_to_last_line_displayed + 1
                    next_line = self._lines[next_line_index]
                    self._write_next_line_as_wrapped(next_line, wrapper)
                    self._index_to_first_line_displayed -= 1
            else:
                self._window.clear()
                self._index_to_last_line_displayed = index_to_first - 1
                for index in range(index_to_first, index_to_last + 1):
                    next_line = self._lines[index]
                    self._write_next_line_as_wrapped(next_line, wrapper)
                self._index_to_first_line_displayed = index_to_first

        if self._resizing:
            _refresh_view(index_to_first, index_to_last, wrapper)
        elif self.autoscroll:
            _refresh_view(None, None, wrapper)
        elif index_to_first is not None:
            _refresh_view(index_to_first, index_to_last, wrapper)

        self._window.touchwin()
        self._window.refresh()

    def redraw(self):
        if not self.autoscroll:
            self._row_of_last_line_displayed = -1
            _, (
                index_corresponding_to_first_line,
                index_corresponding_to_last_line,
            ) = self._find_rows_printable_from_top(self._index_to_first_line_displayed)

            self._window.clear()
        else:
            _, (
                index_corresponding_to_first_line,
                index_corresponding_to_last_line,
            ) = self._find_rows_printable_up_to_last()

            self._window.clear()
        self.refresh_view(
            index_to_first=index_corresponding_to_first_line,
            index_to_last=index_corresponding_to_last_line,
        )

    def resize(self, reconstruct=False):
        if not reconstruct:
            curses.update_lines_cols()
            self._window.resize(curses.LINES, curses.COLS)
            self._set_dimensions()
        else:
            self.reconstruct()
        self._resizing = True
        self.redraw()
        self._resizing = False
