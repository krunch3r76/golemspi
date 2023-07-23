import multiprocessing
import queue
import io
import sys
import select
import threading
import time

from utils.mylogger import console_logger, file_logger


class _StdinListener:
    """functor that asynchronously reads stdin into a buffer and parses lines into
    a shared queue
    """

    def __init__(self, shared_queue: multiprocessing.Queue, stop_event):
        """
        Args:
            shared_queue: asynchronous shared queue
        """
        self.shared_queue = shared_queue
        self.buffer = io.StringIO()
        self.stop_event = stop_event

    def _parse_buffer(self):
        # split lines but preserve incomplete line
        # future proofed in case stdin is not line buffered
        self.buffer.seek(0)
        current_line = self.buffer.readline()
        while current_line.endswith("\n"):
            self.shared_queue.put_nowait(current_line[:-1])
            current_line = self.buffer.readline()
        self.buffer.close()
        self.buffer = io.StringIO()
        self.buffer.write(current_line)  # put partial line back into new buffer

    def read_stdin_line(self):
        line = ""
        while True:
            # Non-blocking read from stdin
            if sys.stdin in select.select([sys.stdin], [], [], 0.01)[0]:
                chunk = sys.stdin.read(1)
                if not chunk:
                    break  # No more data to read
                line += chunk
                if chunk == "\n":
                    self.buffer.write(line)
                    self._parse_buffer()
                    line = ""  # Reset the line for the next input

    def __call__(self):
        while True:
            if self.stop_event.is_set():
                break
            # if ready:
            self.read_stdin_line()


class StdinQueue:
    def __init__(self):
        self.stop_event = threading.Event()
        self._data = multiprocessing.Queue()
        self._stdinListener = _StdinListener(self._data, self.stop_event)
        self._thread = threading.Thread(target=self._stdinListener)
        # self._thread = ExceptableThread(target=self._stdinListener)
        self._thread.start()

    def get_nowait(self):
        try:
            line = self._data.get_nowait()
        except queue.Empty as exc:
            raise exc
        else:
            return line


if __name__ == "__main__":
    stdinQueue = StdinQueue()
    while True:
        try:
            time.sleep(0.01)
            next_line = stdinQueue.get_nowait()
        except queue.Empty:
            pass
        except KeyboardInterrupt:
            stdinQueue.stop_event.set()
            print("joining", flush=True)
            stdinQueue._thread.join()
            break
        else:
            print(f">{next_line}", flush=True)
