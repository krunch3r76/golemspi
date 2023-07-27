import curses
from .ncurses_management import initialize_ncurses, terminate_ncurses
from .ncurses_window import NcursesWindow

from utils.mylogger import console_logger, file_logger


class View:
    def __init__(self):
        self.scr = curses.initscr()
        initialize_ncurses(self.scr)
        self.scr.clear()  # Clears the screen
        self.console_screen = NcursesWindow(
            curses.LINES - 5,  # nlines
            curses.COLS,  # ncols
            5,  # margin_top
            0,  # margin_left
            0,  # margin_bottom
            0,  # margin_right
        )  # Create a new pad that is the size of the entire terminal screen
        self.console_screen.refresh_view()

    def __del__(self):
        terminate_ncurses(self.scr)  # Call the ncurses termination function

    def add_log_line(self, line):
        self.console_screen.add_line(line)
        # self.console_screen.refresh_view()

    def update(self):
        # capture the user's input
        ch = self.scr.getch()

        # check if the user pressed up or down
        if ch == curses.KEY_UP:
            self.console_screen.scroll_up()
        elif ch == curses.KEY_DOWN:
            self.console_screen.scroll_down()

        self.console_screen.refresh_view()

    def update_resources(
        self, threads=None, memory=None, storage=None, subnet=None, init=False
    ):
        pass

    def update_running_exeunit(self, start_time, resource, pid, termination=False):
        pass

    def update_running_exeunit_utilization(self, duration, cpu_percentage, mem_kb):
        pass

    def update_payment_network(self, payment_network, payment_address, token):
        pass
