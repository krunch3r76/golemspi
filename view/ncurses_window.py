# File: golemspi/view/ncurses_window.py
import curses
import textwrap
from view.utils.predicatedlist import PredicatedList
from view.ncurses_management import ColorPair

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
        self._index_to_last_line_displayed = (
            -1
        )  # Track the index of the last displayed line
        self.autoscroll = True
        self._row_of_last_line_displayed = -1

    # def _count_wrapped_lines(self, line):
    #     return len(textwrap.wrap(line, self._win_width))

    def add_line(self, line):
        self._lines.append(line)

    def _blank_rowcount(self):
        return self._win_height - 1 - self._row_of_last_line_displayed

    def _find_rows_printable_up_to_last(self):
        """Return lines and inclusive range from the buffer that, when wrapped, would fill the
        available space.

        This method identifies lines from the buffer that can be wrapped to fit within the available
        space in the window.

        Returns:
            list: A list of lines that can be displayed within the available space.
            tuple: A tuple representing the inclusive range of lines to be displayed, including the indices
                   of the first and last lines that fit within the space.

        Note:
            The method iterates from the last line upwards until it fills the available space or exhausts
            the lines in the buffer.

        """
        rows_available_to_write_to = self._win_height
        line_cursor_bottom = self._index_to_last_line_displayed
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

    def refresh_view(self):
        """
        Refreshes the view of the ncurses window.

        If autoscrolling is enabled (self.autoscroll is True), the method scrolls the content as lines are added.

        If autoscrolling is not enabled, the window is cleared, and the content is drawn without scrolling, showing the lines that can be printed up to the last line.

        This method should be called whenever the view needs to be updated, such as after adding new lines or when scrolling up or down.

        Notes:
            - When autoscrolling, determines new lines by comparing self._index_to_last_line_displayed with
              last offset of self._lines
        """
        from enum import IntEnum

        class TokenPosition(IntEnum):
            TIMESTAMP = 0
            LEVEL = 1
            NAMESPACE = 2

        def rows_available_to_write():
            return self._win_height - 1 - self._row_of_last_line_displayed

        # write wrapped lines scrolling to make space available as needed
        def write_next_line_as_wrapped():
            # post:
            #  self._row_of_last_line_displayed advanced number of lines wrapped
            #  self._index_to_last_line_displayed advanced 1
            next_line_index = self._index_to_last_line_displayed + 1
            next_line = self._lines[next_line_index]
            next_line_wrapped = (
                textwrap.wrap(next_line, self._win_width) if next_line != "" else [""]
            )
            rows_needed_for_writing = len(next_line_wrapped)
            # advance the row cursor to one line beneath last displayed
            row_cursor = self._row_of_last_line_displayed + 1

            # if one row is not enough (no room, more than one line) scroll & adjust row_cursor
            if rows_available_to_write() < rows_needed_for_writing:
                # scroll as many lines as would be needed to write the next wrapped line
                lines_to_scroll = rows_needed_for_writing - rows_available_to_write()
                self._window.scroll(lines_to_scroll)
                row_cursor -= lines_to_scroll

            # write the n lines of the wrapped line list over the (now) available blank rows at bottom
            # post: self._row_of_last_line_displayed incremented n lines
            for line in next_line_wrapped:
                self._window.move(row_cursor, 0)
                if next_line.startswith("[") and "]" in next_line:
                    # Split the line into the bracketed part and the rest
                    bracketed_part, rest_of_line = next_line.split("]", 1)
                    tokens = bracketed_part[1:].split()  # Exclude the opening '['

                    # Write the opening '['
                    self._window.insstr(row_cursor, 0, "[")  # Normal color

                    # Write the first token in light gray
                    self._window.insstr(
                        row_cursor,
                        1,
                        tokens[TokenPosition.TIMESTAMP] + " ",
                        curses.color_pair(ColorPair.LIGHT_GRAY),
                    )

                    offset = len(tokens[TokenPosition.TIMESTAMP]) + 2
                    # Write the second token in appropriate color
                    if tokens[TokenPosition.LEVEL] == "INFO":
                        self._window.insstr(
                            row_cursor,
                            offset,
                            tokens[TokenPosition.LEVEL] + " ",
                            curses.color_pair(ColorPair.INFO),
                        )
                    elif tokens[TokenPosition.LEVEL] == "WARN":
                        self._window.insstr(
                            row_cursor,
                            offset,
                            tokens[TokenPosition.LEVEL] + " ",
                            curses.color_pair(ColorPair.WARN) | curses.A_BOLD,
                        )
                    elif tokens[TokenPosition.LEVEL] == "ERROR":
                        self._window.insstr(
                            row_cursor,
                            offset,
                            tokens[TokenPosition.LEVEL] + " ",
                            curses.color_pair(ColorPair.ERROR),
                        )

                    offset += len(tokens[TokenPosition.LEVEL]) + 1

                    # Write the third token in light gray
                    self._window.insstr(
                        row_cursor,
                        offset,
                        tokens[TokenPosition.NAMESPACE],
                        curses.color_pair(ColorPair.LIGHT_GRAY),
                    )

                    offset += len(tokens[TokenPosition.NAMESPACE])
                    # Write the closing bracket in normal color
                    self._window.insstr(row_cursor, offset, "]", curses.color_pair(0))

                    offset += 1
                    # Write the rest of the line in normal color
                    self._window.insstr(
                        row_cursor, offset, rest_of_line, curses.color_pair(0)
                    )
                else:
                    self._window.insstr(row_cursor, 0, line)

                self._row_of_last_line_displayed = row_cursor
                row_cursor += 1

            # advance reference to index to last line displayed by 1
            self._index_to_last_line_displayed += 1

        if self.autoscroll:
            while self._index_to_last_line_displayed < len(self._lines) - 1:
                write_next_line_as_wrapped()
        else:
            self._window.clear()
            rows_printable_up_to_last, _ = self._find_rows_printable_up_to_last()
            for i, row in enumerate(rows_printable_up_to_last):
                self._window.insstr(i, 0, row)

        # Refreshing the window to display changes
        self._window.refresh()

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

        for _ in range(n):
            _, (
                index_corresponding_to_first_line,
                _,
            ) = self._find_rows_printable_up_to_last()

            if index_corresponding_to_first_line == 0:
                break
            if (
                self._index_to_last_line_displayed - 1 >= 0
                and self._blank_rowcount() == 0
            ):
                self.autoscroll = False
                self._index_to_last_line_displayed -= 1
        curses.napms(10)
        self.refresh_view()

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
        for _ in range(n):
            if (
                self._index_to_last_line_displayed + 1 < len(self._lines)
                and self._blank_rowcount() == 0
            ):
                self._index_to_last_line_displayed += 1
                if self._index_to_last_line_displayed == len(self._lines) - 1:
                    break
        self.refresh_view()
        if self._index_to_last_line_displayed == len(self._lines) - 1:
            self.autoscroll = True
        curses.napms(10)

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
