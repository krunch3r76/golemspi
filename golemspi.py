#!/usr/bin/env python3
# golemspi main

# summary
# the log files give information that can be further abstracted
# to build a model that stores all information that the
# view wants

# the controller interprets the log message to handle
# them as defined events
# these events trigger signals to the model (and view)

import sys

# from pathlib import Path

from controller import Controller
from view import View
from processqueue import FileQueue

# from utils.colors import Colors
from model import Model

from utils.mylogger import file_logger
import signal


def handle_keyboard_interrupt(signal, _):
    try:
        view.shutdown()
    except:
        pass
    sys.exit(signal)


# Register the signal handler for Ctrl+C
signal.signal(signal.SIGINT, handle_keyboard_interrupt)

file_logger.debug("logging started")

if len(sys.argv) == 2:
    cmdline_argument = sys.argv[1]
    str_path_to_log_file = cmdline_argument
    log_queue = FileQueue(str_path_to_log_file)
else:
    raise Exception(
        "golemspi currently does not support piping, please use the included shell script,"
        " which creates an temporary log file that golemspi will parse"
    )

try:
    view = View()
    model = Model()
    controller = Controller(model=model, view=view, log_queue=log_queue)
    # Colors.print_color(f"Reading {str_path_to_log_file}", color=Colors.BLUE_BG)
    # console_logger.debug("hello world")
    controller()
except Exception as e:
    try:
        view.shutdown()  # Assuming that view.shutdown() calls endwin()
    except:
        pass
    file_logger.exception("An exception occurred: %s", e)
except:  # Catch everything else
    file_logger.error(f"Unexpected error: {sys.exc_info()[0]}")
    file_logger.error("Traceback: ", exc_info=True)
