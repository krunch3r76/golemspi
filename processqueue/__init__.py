import os

from .processqueue import ProcessQueue
from .filequeue import FileQueue
from .stdinqueue import StdinQueue
if os.name == "posix":
    from .unixsocketqueue import UnixSocketQueue
