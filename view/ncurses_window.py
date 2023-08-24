# File: golemspi/view/ncurses_window.py
import curses


from utils.mylogger import file_logger


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
