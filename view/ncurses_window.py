# File: golemspi/view/ncurses_window.py
import curses
import textwrap
from view.utils.predicatedlist import PredicatedList
from view.ncurses_management import ColorPair

from utils.mylogger import file_logger


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
        self._resizing = False

    def _set_dimensions(self):
        # Get the total number of lines and columns
        total_lines, total_cols = curses.LINES, curses.COLS

        # Compute the window size based on the margins
        self._win_height = total_lines - self._margin_top - self._margin_bottom
        self._win_width = total_cols - self._margin_left - self._margin_right

    def reconstruct(self):
        file_logger.debug("RECONSTRUCT")
        self._window.clear()
        self._window.refresh()
        del self._window
        self._set_dimensions()

        # Create the window with the computed size
        self._window = curses.newwin(
            self._win_height, self._win_width, self._margin_top, self._margin_left
        )
        self._window.resize(curses.LINES, curses.COLS)
        file_logger.debug("window resized")

    def insstr_truncated(self, row, col, text, attr=None):
        window = self._window
        # Determine the available space for writing
        # available_space = window.getmaxyx()[1] - col
        available_space = self._win_width

        if len(text) > available_space:
            file_logger.debug(f"overwrite by {len(text) - available_space}")
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
    def _write_wrapped_lines(self, row_cursor, next_line_wrapped):
        for i, line in enumerate(next_line_wrapped):
            # file_logger.debug(
            #     f"about to write {line}, rows_available_to_write() -> {rows_available_to_write()}"
            # )
            if i > 0:
                row_cursor += 1
            self._window.move(row_cursor, 0)
            self.insstr_truncated(row_cursor, 0, line)
            self._row_of_last_line_displayed = row_cursor
        return row_cursor

    def reconstruct(self):
        file_logger.debug("RECONSTRUCT")
        super().reconstruct()
        self._window.scrollok(True)

    def _rows_available_to_write(self):
        return self._win_height - 1 - self._row_of_last_line_displayed

    def _write_next_line_as_wrapped(self, next_line, wrapper=None):
        # post:
        #  self._row_of_last_line_displayed advanced number of lines wrapped
        #  self._index_to_last_line_displayed advanced 1

        if wrapper is None:
            wrapper = textwrap.wrap

        virtual_win_width = self._win_width
        next_line_wrapped = (
            wrapper(next_line, virtual_win_width) if next_line != "" else [""]
        )
        if next_line_wrapped[-1] == "":
            next_line_wrapped.pop()

        rows_needed_for_writing = len(next_line_wrapped)

        # advance the row cursor to one line beneath last displayed
        if self._rows_available_to_write() > 0:
            row_cursor = self._row_of_last_line_displayed + 1
        else:
            row_cursor = self._row_of_last_line_displayed

        # if one row is not enough (no room, more than one line) scroll & adjust row_cursor
        if rows_needed_for_writing > self._rows_available_to_write():
            # scroll as many lines as would be needed to write the next wrapped line
            lines_to_scroll = (
                rows_needed_for_writing  # - self._rows_available_to_write()
            )
            self._window.scroll(lines_to_scroll)
            row_cursor -= lines_to_scroll - 1
            self._row_of_last_line_displayed = row_cursor

        row_cursor = self._write_wrapped_lines(row_cursor, next_line_wrapped)
        self._row_of_last_line_displayed = row_cursor

        # advance reference to index to last line displayed by 1
        self._index_to_last_line_displayed += 1

    def refresh_view(self, index_to_first=None, index_to_last=None, wrapper=None):
        """
        Refreshes the view of the ncurses window.

        If autoscrolling is enabled (self.autoscroll is True), the method scrolls the content as lines are added.

        If autoscrolling is not enabled, the window is cleared, and the content is drawn without scrolling, showing the lines that can be printed up to the last line.

        This method should be called whenever the view needs to be updated, such as after adding new lines or when scrolling up or down.

        Notes:
            - When autoscrolling, determines new lines by comparing self._index_to_last_line_displayed with
              last offset of self._lines
        """

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
            self._index_to_first_line_displayed = self._index_to_last_line_displayed
            while self._index_to_last_line_displayed < len(self._lines) - 1:
                next_line_index = self._index_to_last_line_displayed + 1
                next_line = self._lines[next_line_index]
                self._write_next_line_as_wrapped(next_line, wrapper)
                self._index_to_first_line_displayed -= 1
        elif index_to_first is not None:
            self._index_to_last_line_displayed = index_to_first - 1
            self._window.clear()
            for index in range(index_to_first, index_to_last + 1):
                next_line = self._lines[index]
                self._write_next_line_as_wrapped(next_line, wrapper)
            self._index_to_first_line_displayed = index_to_first
        # Refreshing the window to display changes
        self._window.touchwin()
        self._window.refresh()


class NscrollingWindow(NcursesWindowScrolling):
    def __init__(self, margin_top, margin_left, margin_bottom, margin_right):
        super().__init__(margin_top, margin_left, margin_bottom, margin_right)

        self._window.scrollok(True)

        self._lines = PredicatedList()
        self._index_to_last_line_displayed = (
            -1
        )  # Track the index of the last displayed line
        self._index_to_first_line_displayed = -1
        self.autoscroll = True
        self._row_of_last_line_displayed = -1

    def reconstruct(self):
        self._row_of_last_line_displayed = -1
        file_logger.debug("RECONSTRUCT")
        super().reconstruct()

    def _find_rows_printable_up_to_last(self, last_index):
        """Return lines up to the last specified and inclusive range from the buffer that, when wrapped, would fill the
        available space.

        This method identifies lines from the buffer up to _index_to_last_line_displayed
        that can be wrapped to fit within the available space in the window.

        Returns:
            list: A list of lines that can be displayed within the available space.
            tuple: A tuple representing the inclusive range of lines to be displayed, including the indices
                   of the first and last lines that fit within the space.

        Note:
            The method iterates from the last line upwards until it fills the available space or exhausts
            the lines in the buffer.

        """
        rows_available_to_write_to = self._win_height
        line_cursor_bottom = last_index
        line_cursor = line_cursor_bottom
        buffer = []
        while line_cursor >= 0:  # do not try to read lines beyond the first in buffer
            next_line = self._lines[line_cursor]
            # Determine the length of the bracketed expression
            bracketed_expression_length = 0
            if next_line.startswith("[") and "]" in next_line:
                bracketed_expression_length = next_line.index("]") + 1

            # wrap to at least include the bracketed expression
            adjusted_win_length = self._win_width
            if bracketed_expression_length > adjusted_win_length:
                adjusted_win_length = bracketed_expression_length
            if adjusted_win_length < bracketed_expression_length:
                adjusted_win_length = bracketed_expression_length

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
        # self._row_of_last_line_displayed = self._win_height - 1
        # flatten buffer
        wrapped_visible_lines = [line for sublist in buffer for line in sublist]
        return wrapped_visible_lines, (
            line_cursor,
            line_cursor_bottom,
        )

    # def _count_wrapped_lines(self, line):
    #     return len(textwrap.wrap(line, self._win_width))

    def add_line(self, line):
        """Add a line to the internal buffer


        Notes:
            refresh_view must be called externally to reflect any changes
        """
        self._lines.append(line)

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

    def _blank_rowcount(self):
        return self._win_height - 1 - self._row_of_last_line_displayed

    def _find_rows_printable_from_top(self, top_index=0):
        """Return lines from the top and inclusive range from the buffer that, when wrapped, would fill the available space."""
        rows_available_to_write_to = self._win_height
        line_cursor_top = 0
        line_cursor = line_cursor_top

        buffer = []
        while (
            line_cursor <= self._win_height - 1
            and top_index + line_cursor < len(self._lines) - 1
        ):
            next_line = self._lines[top_index + line_cursor]
            # Determine the length of the bracketed expression
            bracketed_expression_length = 0
            if next_line.startswith("[") and "]" in next_line:
                bracketed_expression_length = next_line.index("]") + 1

            # wrap to at least include the bracketed expression
            adjusted_win_length = self._win_width
            if bracketed_expression_length > adjusted_win_length:
                adjusted_win_length = bracketed_expression_length
            if adjusted_win_length < bracketed_expression_length:
                adjusted_win_length = bracketed_expression_length

            next_wrapped_line = textwrap.wrap(next_line, adjusted_win_length)
            count_lines_needed = len(next_wrapped_line)
            if count_lines_needed <= rows_available_to_write_to:
                buffer.append(next_wrapped_line)
                rows_available_to_write_to -= count_lines_needed
            else:
                break
            line_cursor += 1
        wrapped_visible_lines = [line for sublist in buffer for line in sublist]
        return wrapped_visible_lines, (line_cursor_top, line_cursor - 1)

    def _write_wrapped_lines(self, row_cursor, next_line_wrapped):
        # write the n lines of the wrapped line list over the (now) available blank rows at bottom
        # post: self._row_of_last_line_displayed incremented n lines

        from enum import IntEnum

        class TokenPosition(IntEnum):
            TIMESTAMP = 0
            LEVEL = 1
            NAMESPACE = 2

        for i, line in enumerate(next_line_wrapped):
            if i > 0:
                row_cursor += 1
            self._window.move(row_cursor, 0)
            if i == 0 and line.startswith("[") and "[" in line and line.startswith("["):
                # Split the line into the bracketed part and the rest
                bracketed_part, rest_of_line = line.split("]", 1)
                tokens = bracketed_part[1:].split()  # Exclude the opening '['
                offset = 0
                # Write the opening '['
                offset += self.insstr_truncated(row_cursor, offset, "[")  # Normal color

                # Write the first token in light gray
                offset += self.insstr_truncated(
                    row_cursor,
                    offset,
                    tokens[TokenPosition.TIMESTAMP] + " ",
                    curses.color_pair(ColorPair.DARK_GRAY),
                )

                # offset = len(tokens[TokenPosition.TIMESTAMP]) + 2
                # Write the second token in appropriate color
                if tokens[TokenPosition.LEVEL] == "INFO":
                    offset += self.insstr_truncated(
                        row_cursor,
                        offset,
                        tokens[TokenPosition.LEVEL] + " ",
                        curses.color_pair(ColorPair.INFO),
                    )
                elif tokens[TokenPosition.LEVEL] == "WARN":
                    offset += self.insstr_truncated(
                        row_cursor,
                        offset,
                        tokens[TokenPosition.LEVEL] + " ",
                        curses.color_pair(ColorPair.WARN),
                    )
                elif tokens[TokenPosition.LEVEL] == "ERROR":
                    offset += self.insstr_truncated(
                        row_cursor,
                        offset,
                        tokens[TokenPosition.LEVEL] + " ",
                        curses.color_pair(ColorPair.ERROR),
                    )

                # Write the third token in light gray
                offset += self.insstr_truncated(
                    row_cursor,
                    offset,
                    tokens[TokenPosition.NAMESPACE],
                    curses.color_pair(ColorPair.DARK_GRAY),
                )

                # Write the closing bracket in normal color
                offset += self.insstr_truncated(row_cursor, offset, "]")

                # Write the rest of the line in normal color
                self.insstr_truncated(row_cursor, offset, rest_of_line)
            else:
                self.insstr_truncated(row_cursor, 0, line)

        return row_cursor

    def refresh_view(self, index_to_first=None, index_to_last=None):
        """
        Refreshes the view of the ncurses window.

        If autoscrolling is enabled (self.autoscroll is True), the method scrolls the content as lines are added.

        If autoscrolling is not enabled, the window is cleared, and the content is drawn without scrolling, showing the lines that can be printed up to the last line.

        This method should be called whenever the view needs to be updated, such as after adding new lines or when scrolling up or down.

        Notes:
            - When autoscrolling, determines new lines by comparing self._index_to_last_line_displayed with
              last offset of self._lines
        """

        def mywrapper(next_line, virtual_win_width):
            # Determine the length of the bracketed expression
            bracketed_expression_length = 0
            if next_line.startswith("[") and "]" in next_line:
                bracketed_expression_length = next_line.index("]") + 1

            # wrap to at least include the bracketed expression
            adjusted_win_length = self._win_width
            if bracketed_expression_length > adjusted_win_length:
                adjusted_win_length = bracketed_expression_length
            if adjusted_win_length < bracketed_expression_length:
                adjusted_win_length = bracketed_expression_length
            next_line_wrapped = (
                textwrap.wrap(next_line, adjusted_win_length)
                if next_line != ""
                else [""]
            )
            return next_line_wrapped

        super().refresh_view(index_to_first, index_to_last, mywrapper)

    def redraw(self):
        # self._window.touchwin()
        # self._window.refresh()
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
        # self._window.clear()
        # self._window.redrawwin()

    def scroll_up(self, n=1):
        """Scrolls the window up by n number of lines.

        This method scrolls the console window up by n lines, or up to n lines if there are fewer lines
        available above the current top line. If the window is already scrolled to the top, no action is
        taken.

        Args:
            n (int, optional): The number of lines to scroll up. Defaults to 1.

        Note:
            If autoscrolling is active and the window scrolls up, autoscrolling will be turned off.

        Post-State:
            The console window is redrawn to display the content after scrolling, with the new top line
            reflecting the scrolling action.
        """

        CHANGE = False
        index_corresponding_to_first_line = None
        index_corresponding_to_last_line = None

        previous_index_to_last_line_displayed = self._index_to_last_line_displayed - 1

        if self._index_to_first_line_displayed == 0:
            return

        for _ in range(n):
            _, (
                index_corresponding_to_first_line,
                index_corresponding_to_last_line,
            ) = self._find_rows_printable_up_to_last(
                previous_index_to_last_line_displayed
            )

            previous_index_to_last_line_displayed -= 1

            if (
                previous_index_to_last_line_displayed >= 0
                and self._blank_rowcount() == 0
            ):
                self.autoscroll = False
                CHANGE = True
        curses.napms(10)
        if CHANGE:
            self.refresh_view(
                index_to_first=index_corresponding_to_first_line,
                index_to_last=index_corresponding_to_last_line,
            )

    def scroll_down(self, n=1):
        """Scrolls the window down by n number of lines.

        This method scrolls the console window down by n lines, or up to n lines if there are fewer lines
        available below the current bottom line. If the window is already scrolled to the bottom, no action
        is taken.

        Args:
            n (int, optional): The number of lines to scroll down. Defaults to 1.

        Note:
            If autoscrolling is inactive and the window scrolls to the last line, autoscrolling will be
            turned on.

        Post-State:
            The console window is redrawn to display the content after scrolling, with the new bottom line
            reflecting the scrolling action.
        """

        #        CHANGE = False
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
        curses.napms(10)

    def resize(self, reconstruct=False):
        if not reconstruct:
            curses.update_lines_cols()
            self._window.resize(curses.LINES, curses.COLS)
            self._set_dimensions()
        else:
            self.reconstruct()
        # self.reconstruct()
        self._resizing = True


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
