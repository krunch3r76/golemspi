# controller/events/log_events/new_task_event.py


from ..log_line import LogLine
from ..event import Event

import re
from pathlib import Path


class NewTaskEvent(Event):
    def __init__(
        self,
        timestamp,
        agreement_hash,
        activity_hash,
        path_to_work_dir,
        path_to_agreement_dir,
        path_to_agreement_json_file,
        path_to_activity_dir,
        path_to_deployment_json_file,
    ):
        super().__init__(timestamp)
        self.timestamp = timestamp
        self.agreement_hash = agreement_hash
        self.activity_hash = activity_hash
        self.path_to_work_dir = path_to_work_dir
        self.path_to_agreement_dir = path_to_agreement_dir
        self.path_to_agreement_json_file = path_to_agreement_json_file
        self.path_to_activity_dir = path_to_activity_dir
        self.path_to_deployment_json_file = path_to_deployment_json_file

    @classmethod
    def from_log_line(cls, log_line):
        """
        [2023-05-29T01:21:06.645-0700 INFO  ya_provider::execution::task_runner] Creating task: agreement [a20c1e8861638bfd9120ba3088b270b6f2b33aae0fd6ad479ba6e81a0fbe9f00], activity [225e48e33e2a4c429af6c836f1a29a8e] in directory: [/home/golem/.local/share/ya-provider/exe-unit/work/a20c1e8861638bfd9120ba3088b270b6f2b33aae0fd6ad479ba6e81a0fbe9f00/225e48e33e2a4c429af6c836f1a29a8e].
        """

        pattern = re.compile(
            r"""
            \[ (?P<agreement_hash> [\w]+) \] \s? , \s?
            activity \s? \[ (?P<activity_hash> [\w]+) \] \s?
            in \s directory: \s \[ (?P<directory> [^\]]+) \]
            """,
            re.X,
        )

        match = pattern.search(log_line.message)

        if not match:
            return None

        agreement_hash = match.group("agreement_hash")
        activity_hash = match.group("activity_hash")
        directory = match.group("directory")

        directory_path = Path(directory)
        path_to_activity_dir = Path(directory_path)
        path_to_agreement_dir = path_to_activity_dir.parent
        path_to_work_dir = path_to_agreement_dir.parent
        path_to_agreement_json_file = path_to_agreement_dir / "agreement.json"
        path_to_deployment_json_file = path_to_activity_dir / "agreement.json"

        # Create a new instance of NewTaskEvent
        return cls(
            log_line.timestamp,
            agreement_hash,
            activity_hash,
            str(path_to_work_dir),
            str(path_to_agreement_dir),
            str(path_to_agreement_json_file),
            str(path_to_activity_dir),
            str(path_to_deployment_json_file),
        )
