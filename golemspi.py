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
from pathlib import Path

from controller import Controller
from view import View
from processqueue import FileQueue, StdinQueue
from utils.colors import Colors
from model import Model
from utils.mylogger import console_logger, file_logger
import signal

def handle_keyboard_interrupt(signal, frame):
    if 'log_queue' in globals():
        try:
            log_queue._thread.join()  # Call join on log_queue thread here
        except:
            pass
    sys.exit(0)


# Register the signal handler for Ctrl+C
signal.signal(signal.SIGINT, handle_keyboard_interrupt)

if len(sys.argv) == 2:
    cmdline_argument = sys.argv[1]
    str_path_to_log_file = cmdline_argument
    log_queue = FileQueue(str_path_to_log_file)
else:
    log_queue = StdinQueue()
view = View()
model = Model()
controller = Controller(model=model, view=view, log_queue=log_queue)
# Colors.print_color(f"Reading {str_path_to_log_file}", color=Colors.BLUE_BG)
# console_logger.debug("hello world")
controller()
