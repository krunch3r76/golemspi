# File: golemspi/view/ncurses_management.py

import curses


def initialize_ncurses(scr):
    curses.noecho()  # intercept don't display
    curses.cbreak()  # non-buffered input
    curses.curs_set(0)
    scr.nodelay(True)  # make getch non-blocking
    scr.scrollok(True)
    scr.keypad(True)
    curses.delay_output(100)
    curses.start_color()
    curses.init_pair(
        1, curses.COLOR_YELLOW, curses.COLOR_BLACK
    )  # Use COLOR_BLACK for deep black background


def terminate_ncurses(scr):
    curses.nocbreak()
    scr.keypad(False)
    curses.echo()
    curses.curs_set(1)
    curses.endwin()
