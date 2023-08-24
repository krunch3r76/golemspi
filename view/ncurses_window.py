# File: golemspi/view/ncurses_window.py
import curses
import textwrap
from view.utils.predicatedlist import PredicatedList
from view.ncurses_management import ColorPair

from utils.mylogger import file_logger
import inspect


class _NcursesWindow:
    def __init__(self, margin_top, margin_left, margin_bottom, margin_right):
        self._margin_top = margin_top
        self._margin_left = margin_left
        self._margin_bottom = margin_bottom
        self._margin_right = margin_right
        self._window = None
        _NcursesWindow.reconstruct(self)
        self._resizing = False

    def _set_dimensions(self):
        # Get the total number of lines and columns
        total_lines, total_cols = curses.LINES, curses.COLS

        # Compute the window size based on the margins
        self._win_height = total_lines - self._margin_top - self._margin_bottom
        self._win_width = total_cols - self._margin_left - self._margin_right

    def reconstruct(self):
        if self._window is not None:
            self._window.clear()
            self._window.refresh()
            del self._window

        self._set_dimensions()

        # Create the window with the computed size
        self._window = curses.newwin(
            self._win_height, self._win_width, self._margin_top, self._margin_left
        )
        self._window.resize(curses.LINES, curses.COLS)

    def insstr_truncated(self, row, col, text, attr=None):
        window = self._window
        # Determine the available space for writing
        available_space = self._win_width - col

        if available_space == 0:
            return 0

        # Truncate the text if necessary
        truncated_text = text[:available_space]

        # Write the text, applying the attribute if provided
        if attr is not None:
            window.insstr(row, col, truncated_text, attr)
        else:
            window.insstr(row, col, truncated_text)
        # Return the length of the text that was actually written
        return len(truncated_text)


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
        for i, line in enumerate(next_line_wrapped):
            self._window.move(row_cursor, 0)
            self.insstr_truncated(row_cursor, 0, line)
            self._row_of_last_line_displayed = row_cursor
            row_cursor += 1
        return row_cursor - 1

    def reconstruct(self):
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

        CHANGE = False
        index_corresponding_to_first_line = None
        index_corresponding_to_last_line = None

        for _ in range(n):
            previous_index_to_last_line_displayed = (
                self._index_to_last_line_displayed - 1
            )
            _, (
                index_corresponding_to_first_line,
                index_corresponding_to_last_line,
            ) = self._find_rows_printable_up_to_last(
                previous_index_to_last_line_displayed
            )
            self._index_to_last_line_displayed -= 1
            if (
                previous_index_to_last_line_displayed >= 0
                and self._blank_rowcount() == 0
            ):
                self.autoscroll = False
                CHANGE = True
            if index_corresponding_to_first_line == 0:
                break

        curses.napms(1)
        if CHANGE or index_corresponding_to_first_line == 0:
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
        curses.napms(1)

    def _rows_available_to_write(self):
        # if self._row_of_last_line_displayed == None:
        #     return self._win_height - 1
        if self._row_of_last_line_displayed == -1:
            return self._win_height

        return self._win_height - self._row_of_last_line_displayed - 1

    def _write_next_line_as_wrapped(self, next_line, wrapper=None):
        if wrapper is None:
            wrapper = textwrap.wrap

        virtual_win_width = self._win_width
        next_line_wrapped = (
            wrapper(next_line, virtual_win_width) if next_line != "" else [""]
        )
        while next_line_wrapped[-1] == "":
            # if next_line_wrapped[-1] == "":
            next_line_wrapped.pop()
            file_logger.debug("POP!------------------")

        rows_needed_for_writing = len(next_line_wrapped)

        if (
            rows_needed_for_writing
            > self._rows_available_to_write()
            # and not self._resizing
        ):
            # not self_resizing should be implied if pre conditions are correct!
            # scroll as many lines as would be needed to write the next wrapped line
            lines_to_scroll = rows_needed_for_writing - self._rows_available_to_write()
            # file_logger.debug(f"SCROLLING {lines_to_scroll} lines")
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

            if fnc_line_min_length is not None:
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

    def refresh_view(
        self, index_to_first=None, index_to_last=None, wrapper=None, clear=False
    ):
        # write wrapped lines scrolling to make space available as needed
        if self._resizing:
            self._index_to_last_line_displayed = index_to_first - 1  # proactive
            for index in range(index_to_first, index_to_last + 1):
                next_line = self._lines[index]
                self._write_next_line_as_wrapped(next_line, wrapper)
            if self._index_to_last_line_displayed == len(self._lines) - 1:
                self.autoscroll = True
            self._resizing = False
            self._index_to_first_line_displayed = index_to_first
        elif self.autoscroll:
            # reimplement to count lines drawable up to last in buffer
            self._index_to_first_line_displayed = self._index_to_last_line_displayed
            if clear:
                self._window.clear()
            while self._index_to_last_line_displayed < len(self._lines) - 1:
                next_line_index = self._index_to_last_line_displayed + 1
                next_line = self._lines[next_line_index]
                self._write_next_line_as_wrapped(next_line, wrapper)
                self._index_to_first_line_displayed -= 1
        elif index_to_first is not None:
            self._index_to_last_line_displayed = index_to_first - 1
            self._row_of_last_line_displayed = -1
            self._window.clear()
            for index in range(index_to_first, index_to_last + 1):
                next_line = self._lines[index]
                self._write_next_line_as_wrapped(next_line, wrapper)
            self._index_to_first_line_displayed = index_to_first
        # Refreshing the window to display changes
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
            self.refresh_view(
                index_to_first=index_corresponding_to_first_line,
                index_to_last=index_corresponding_to_last_line,
            )
        else:
            _, (
                index_corresponding_to_first_line,
                index_corresponding_to_last_line,
            ) = self._find_rows_printable_up_to_last()

            self._window.clear()
            self.refresh_view(
                index_to_first=index_corresponding_to_first_line,
                index_to_last=index_corresponding_to_last_line,
                clear=True,
            )

    def resize(self, reconstruct=False):
        if not reconstruct:
            curses.update_lines_cols()
            self._window.resize(curses.LINES, curses.COLS)
            self._set_dimensions()
        else:
            self.reconstruct()
        self._resizing = True


class GolemSPLogScrollingWindow(NcursesWindowScrolling):
    def __init__(
        self,
        margin_top,
        margin_left,
        margin_bottom,
        margin_right,
        line_buffer_class=None,
    ):
        if line_buffer_class is None:
            line_buffer_class = PredicatedList
        super().__init__(
            margin_top,
            margin_left,
            margin_bottom,
            margin_right,
            line_buffer_class=line_buffer_class,
        )

    def _adjusted_win_length(self, next_line):
        """logic to specify a minimum window length based on the line content to prevent wrapping

        notes: the class handles this case by truncating what would not wrap
        """

        # Determine the length of the bracketed expression
        bracketed_expression_length = (
            next_line.index("]") + 1
            if next_line.startswith("[") and "]" in next_line
            else 0
        )

        # wrap to at least include the bracketed expression
        return max(self._win_width, bracketed_expression_length)

    def _find_rows_printable_up_to_last(self, last_index=None):
        """Return wrapped lines and inclusive range of indices that could be written to the current window ending in the line at the specified index"""
        if last_index is None:
            last_index = len(self._lines) - 1
        return super()._find_rows_printable_up_to_last(
            last_index, self._adjusted_win_length
        )

    def _find_rows_printable_from_top(self, top_index=0):
        """Return wrapped lines and inclusive range of indices that could be written to the current window starting from the specific top index"""
        return super()._find_rows_printable_from_top(
            top_index, self._adjusted_win_length
        )

    def _write_wrapped_lines(self, row_cursor, next_line_wrapped):
        """write lines as wrapped starting at row cursor"""

        def _parse_tokens(line):
            from enum import IntEnum

            class TokenPosition(IntEnum):
                TIMESTAMP = 0
                LEVEL = 1
                NAMESPACE = 2

            def _get_color_for_level(level):
                if level == "INFO":
                    return curses.color_pair(ColorPair.INFO)
                elif level == "WARN":
                    return curses.color_pair(ColorPair.WARN)
                elif level == "ERROR":
                    return curses.color_pair(ColorPair.ERROR)
                return curses.color_pair(ColorPair.DEFAULT)

            # Split the line into the bracketed part and the rest
            bracketed_part, rest_of_line = line.split("]", 1)
            tokens = bracketed_part[1:].split()  # Exclude the opening '['

            # Determine the color for each token
            token_colors = [
                curses.color_pair(ColorPair.DARK_GRAY),  # TIMESTAMP
                _get_color_for_level(tokens[TokenPosition.LEVEL]),  # LEVEL
                curses.color_pair(ColorPair.DARK_GRAY),
            ]  # NAMESPACE

            return tokens, token_colors, rest_of_line

        for i, line in enumerate(next_line_wrapped):
            self._window.move(row_cursor, 0)
            if i == 0 and line.startswith("[") and "]" in line:
                tokens, token_colors, rest_of_line = _parse_tokens(line)
                offset = 0
                # Write the opening '['
                offset += self.insstr_truncated(row_cursor, offset, "[")  # Normal color

                # Write the tokens
                for j, token in enumerate(tokens):
                    offset += self.insstr_truncated(
                        row_cursor, offset, token + " ", token_colors[j]
                    )

                # Write the closing bracket in normal color
                offset += self.insstr_truncated(row_cursor, offset, "]")

                # Write the rest of the line in normal color
                self.insstr_truncated(row_cursor, offset, rest_of_line)
            else:
                self.insstr_truncated(row_cursor, 0, line)
            row_cursor += 1

        return row_cursor - 1

    def refresh_view(self, index_to_first=None, index_to_last=None, clear=False):
        """update the window and optionally specify lines to write to the window and whether to clear

        notes: clear is only used in the case of auto-scrolling (specifically from the resize event)
        """

        def mywrapper(next_line, virtual_win_width):
            # wrap to at least include the bracketed expression
            adjusted_win_length = self._adjusted_win_length(next_line)
            next_line_wrapped = (
                textwrap.wrap(next_line, adjusted_win_length)
                if next_line != ""
                else [""]
            )
            return next_line_wrapped

        super().refresh_view(index_to_first, index_to_last, mywrapper, clear=clear)
