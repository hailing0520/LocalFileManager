from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class RunMode(str, Enum):
    DRY_RUN = "dry-run"
    APPLY = "apply"


class FileActionType(str, Enum):
    CREATE_FOLDER = "create_folder"
    MOVE_FILE = "move_file"
    RENAME_FILE = "rename_file"
    DELETE_FILE = "delete_file"
    CLASSIFY_ONLY = "classify_only"


@dataclass
class UserIntent:
    raw_text: str
    target_path: Path
    run_mode: RunMode = RunMode.DRY_RUN


@dataclass
class FileItem:
    path: Path
    extension: str
    category: str = "other"


@dataclass
class ActionPlanItem:
    action_type: FileActionType
    source: Path | None = None
    destination: Path | None = None
    reason: str = ""


@dataclass
class PipelineContext:
    intent: UserIntent
    files: list[FileItem] = field(default_factory=list)
    plans: list[ActionPlanItem] = field(default_factory=list)
    logs: list[str] = field(default_factory=list)
    unsupported: list[Path] = field(default_factory=list)

