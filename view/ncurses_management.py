# File: golemspi/view/ncurses_management.py
from enum import auto, IntEnum
import curses


class Color(IntEnum):
    LIGHT_GRAY = 200
    CUSTOM_YELLOW = auto()
    ORANGE = auto()


def init_color_from_hex(color_number, hex_code):
    # Convert the hexadecimal code to integer values
    red = int(hex_code[0:2], 16)
    green = int(hex_code[2:4], 16)
    blue = int(hex_code[4:6], 16)

    # Scale the values to the range 0-1000, as expected by init_color()
    red = int((red / 255) * 1000)
    green = int((green / 255) * 1000)
    blue = int((blue / 255) * 1000)

    # Call init_color() with the scaled values
    curses.init_color(color_number, red, green, blue)


class ColorPair(IntEnum):
    LIGHT_GRAY = 1
    INFO = auto()
    WARN = auto()
    ERROR = auto()


def initialize_ncurses(scr):
    curses.noecho()  # intercept don't display
    curses.cbreak()  # non-buffered input
    curses.curs_set(0)
    scr.nodelay(True)  # make getch non-blocking
    scr.scrollok(True)
    scr.keypad(True)
    curses.delay_output(100)
    curses.start_color()
    curses.use_default_colors()

    # Define light gray color
    # curses.init_color(Color.LIGHT_GRAY, 700, 700, 700)  # Corresponds to #d3d3d3
    # curses.init_color(Color.CUSTOM_YELLOW, 1000, 1000, 0)
    # curses.init_color(Color.ORANGE, 1000, 647, 0)
    init_color_from_hex(Color.LIGHT_GRAY, "d3d3d3")
    init_color_from_hex(Color.CUSTOM_YELLOW, "ffff00")
    init_color_from_hex(Color.ORANGE, "ffa500")

    curses.init_pair(ColorPair.LIGHT_GRAY, Color.LIGHT_GRAY, -1)
    curses.init_pair(ColorPair.INFO, curses.COLOR_GREEN, -1)
    curses.init_pair(ColorPair.WARN, curses.COLOR_YELLOW, -1)
    curses.init_pair(ColorPair.ERROR, curses.COLOR_RED, -1)
    # curses.init_pair(
    #     1, curses.COLOR_YELLOW, curses.COLOR_BLACK
    # )  # Use COLOR_BLACK for deep black background


def terminate_ncurses(scr):
    curses.nocbreak()
    scr.keypad(False)
    curses.echo()
    curses.curs_set(1)
    curses.endwin()
