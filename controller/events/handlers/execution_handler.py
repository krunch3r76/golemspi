# controller/events/handlers/execution_handler.py
from ..event import Event
from ..log_line import LogLine
from ..log_events import (
    NewTaskEvent,
    NewExeUnitLogsDirEvent,
    NewExeUnitPidEvent,
    ExeUnitTerminatedEvent,
    ExeUnitExitedEvent,
)


def identify_event_class(log_line: LogLine):
    # event_class = Event(log_line.timestamp)  # Identify the appropriate event class
    if log_line.message.startswith("Creating task"):
        """
        [2023-05-29T01:21:06.645-0700 INFO  ya_provider::execution::task_runner] Creating task: agreement [a20c1e8861638bfd9120ba3088b270b6f2b33aae0fd6ad479ba6e81a0fbe9f00], activity [225e48e33e2a4c429af6c836f1a29a8e] in directory: [/home/golem/.local/share/ya-provider/exe-unit/work/a20c1e8861638bfd9120ba3088b270b6f2b33aae0fd6ad479ba6e81a0fbe9f00/225e48e33e2a4c429af6c836f1a29a8e].
        """
        return NewTaskEvent.from_log_line(log_line)
    elif log_line.message.startswith("Exeunit log directory"):
        return NewExeUnitLogsDirEvent.from_log_line(log_line)
        """
        [2023-05-29T01:21:06.645-0700 INFO  ya_provider::execution::exeunit_instance] Exeunit log directory: /home/golem/.local/share/ya-provider/exe-unit/work/a20c1e8861638bfd9120ba3088b270b6f2b33aae0fd6ad479ba6e81a0fbe9f00/225e48e33e2a4c429af6c836f1a29a8e/logs
        """
    elif log_line.message.startswith("Exeunit process spawned"):
        """[2023-05-29T01:21:06.646-0700 INFO  ya_provider::execution::exeunit_instance] Exeunit process spawned, pid: 486619"""
        return NewExeUnitPidEvent.from_log_line(log_line)
    elif log_line.message.startswith("ExeUnit for activity terminated"):
        """[2023-05-29T08:11:51.880-0700 INFO  ya_provider::execution::task_runner] ExeUnit for activity terminated: [94ffdb99fcd4467ea489218a8ce3cb2a]."""
        return ExeUnitTerminatedEvent.from_log_line(log_line)
    elif log_line.message.startswith("ExeUnit process exited with status"):
        """[2023-05-29T08:11:51.880-0700 INFO  ya_provider::execution::task_runner] ExeUnit process exited with status Finished - exit status: 0, agreement [db5506e88ff312070eca87147d445dc0ce6084723c3f41158e1f7b9e72ece679], activity [94ffdb99fcd4467ea489218a8ce3cb2a]."""
        return ExeUnitExitedEvent.from_log_line(log_line)
    return None
