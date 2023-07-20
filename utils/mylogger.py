try:
    from mylogger import console_logger, file_logger
except:
    import logging

    console_logger = logging.getLogger(__name__)
    console_logger.addHandler(logging.NullHandler())
    file_logger = console_logger
