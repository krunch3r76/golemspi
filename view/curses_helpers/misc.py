import curses

# from .get_printable_range import get_printable_range
# from .paddedwindow import PaddedWindow

# sane_screen_defaults(scr)
# terminate_curses(scr)
# resize_on_key_resize(scr)
# print_in_middle(win, starty, startx, width, string, color)
# win_show(win, label, label_color=1)
# rows_occupied(countCol, line)

from utils.mylogger import file_logger


def ordinal_for_control_char(control_char):
    # compute the ordinal for the ctrl character sequence including control_char
    return ord(control_char) - ord("a") + 1


def sane_screen_defaults(scr):
    # set up common defaults for the window object representing the entire screen
    # pre: initscr() called on scr
    curses.noecho()  # intercept don't display
    curses.cbreak()  # non-buffered input
    curses.curs_set(0)
    curses.start_color()
    scr.nodelay(True)  # make getch non-blocking
    scr.scrollok(True)
    scr.keypad(True)
    curses.delay_output(100)
    curses.start_color()
    curses.init_pair(
        1, curses.COLOR_YELLOW, curses.COLOR_BLACK
    )  # Use COLOR_BLACK for deep black background
    # curses.init_pair(
    #     2, curses.A_NORMAL, curses.A_NORMAL
    # )  # Use COLOR_BLACK for deep black background
    # scr.bkgd(curses.color_pair(2))


def terminate_curses(scr):
    # restore defaults
    curses.nocbreak()
    scr.keypad(False)
    curses.echo()
    curses.curs_set(1)
    curses.endwin()


def resize_on_key_resize(scr, subwindows=None, resizing=False):
    # update ncurses on a new "screen" size

    # this is useful to prevent windows from throwing an exception when
    # the drawable area is not aligned with the actual drawable area
    # for example, a line written beyond the actual columns available
    # will throw but this is not the case as long as the underlying
    # screen is correctly updated no matter how long / how many columns
    curses.update_lines_cols()
    # curses.resizeterm(curses.LINES, curses.COLS)
    scr.resize(curses.LINES, curses.COLS)
    # curses.doupdate()
    if subwindows is not None:
        for subwindow in subwindows:
            # subwindow.clear()
            subwindow.resize_fit()
            # subwindow.redrawwin()
        scr.clear()  # clear artifacts from subwindows
        scr.noutrefresh()
        for subwindow in subwindows:
            # subwindow.redrawwin()
            subwindow.redraw()
        curses.napms(100)
    return True


# credit: from python_ncurses_examples
def print_in_middle(win, starty, startx, width, string, color):
    """Print a string in the middle of a window"""
    y, x = win.getyx()

    if startx != 0:
        x = startx

    if starty != 0:
        y = starty

    if width == 0:
        width = 80

    length = len(string)
    temp = (width - length) // 2
    x = startx + temp
    win.attron(color)
    win.addstr(y, x, string)
    win.attroff(color)
    win.refresh()


# credit: from python_ncurses_examples
def win_show(win, label, label_color=1):
    """Show the window with a border and a label"""
    starty, startx = win.getbegyx()
    height, width = win.getmaxyx()

    win.box(0, 0)
    win.addch(2, 0, curses.ACS_LTEE)
    win.hline(2, 1, curses.ACS_HLINE, width - 2)
    win.addch(2, width - 1, curses.ACS_RTEE)

    print_in_middle(win, 1, 0, width, label, curses.color_pair(label_color))
