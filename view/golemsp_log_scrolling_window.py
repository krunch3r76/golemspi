from .ncurses_window_scrolling import NcursesWindowScrolling
from view.ncurses_management import ColorPair

import textwrap
import curses

from utils.mylogger import file_logger
from view.ncurses_management import ColorPair


class GolemSPLogScrollingWindow(NcursesWindowScrolling):
    def __init__(
        self,
        margin_top,
        margin_left,
        margin_bottom,
        margin_right,
        line_buffer_class=None,
    ):
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
