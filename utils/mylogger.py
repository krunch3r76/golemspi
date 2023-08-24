import inspect

try:
    from mylogger import console_logger, file_logger
except ModuleNotFoundError:
    import logging

    console_logger = logging.getLogger(__name__)
    console_logger.addHandler(logging.NullHandler())
    file_logger = console_logger


def printf_calling_function():
    # Get the current frame
    current_frame = inspect.currentframe()
    # Go back two frames to find the caller of the function that called this function
    calling_frame = inspect.getouterframes(current_frame, 2)[2][0]
    # Get the information about the calling function
    info = inspect.getframeinfo(calling_frame)
    return f"Called from {info.function} in file {info.filename} on line {info.lineno}"
