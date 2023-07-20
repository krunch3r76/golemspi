# ./model/objects/version_info.py
from dataclasses import dataclass


@dataclass
class VersionInfo:
    timestamp: int
    version: str
    commit: str
    build_date: str
    build_number: int
