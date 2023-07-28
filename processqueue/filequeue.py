# filequeue.py
"""tail a file in a separate thread to read line by line into a shared queue

exports FileQueue that wraps a python Queue object exposing get_nowait()
the queue is filled by all lines in the file which is monitored for additional data

author: krunch3r (KJM github.com/krunch3r76)
license: General Poetic License (GPL3)

"""

from pathlib import Path
import multiprocessing
import io
import time

from utils.mylogger import console_logger, file_logger


def _strip_ansi(text):
    # strip ansi codes from text and return
    # credit. chat.openai.com
    import re

    stripped_text = re.sub(r"\x1B\[[0-?]*[ -/]*[@-~]", "", text)
    return stripped_text


class ReadLineBuffer:
    def __init__(self, target_text_file, on_complete_line):
        self.target_text_file = target_text_file
        self.on_complete_line = on_complete_line

    def __call__(self):
        while True:
            time.sleep(0.01)
            line = self.target_text_file.readline()
            if line:
                if not line.strip():
                    line = ""
                self.on_complete_line(line)


class FileQueue:
    # open a file and queue lines as they become available (tail)

    def __init__(self, path_to_file):
        """
        Args:
            path_to_file: a path as input to a python pathlib.Path object
        """
        self._pathFile = Path(path_to_file)
        self._queueShared = multiprocessing.Queue()
        self._fileOpen = self._pathFile.open(mode="r")
        self._readLineBuffer = ReadLineBuffer(
            self._fileOpen, lambda line: self._queueShared.put_nowait(line)
        )
        self._multiprocess = multiprocessing.Process(
            target=self._readLineBuffer, daemon=True
        )
        self._multiprocess.start()

    def get_nowait(self):
        """call get_nowait on wrapped Queue
        Raises:
            queue.Empty on an empty queue
        """
        next_line = self._queueShared.get_nowait()
        if next_line is not None:
            next_line = _strip_ansi(next_line)
        return next_line


if __name__ == "__main__":
    import sys
    import time
    import queue

    fileQueue = FileQueue(sys.argv[1])

    while True:
        try:
            line = fileQueue.get_nowait()
        except queue.Empty:
            time.sleep(0.001)
        else:
            print(line)
