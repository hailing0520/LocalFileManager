from __future__ import annotations

from pathlib import Path

from localfilemanager.models import ActionPlanItem, FileActionType


class LocalFileSystemMCP:
    """
    MCP adapter for local file system.
    V1 intentionally uses placeholders for critical operations.
    """

    def execute(self, plan: ActionPlanItem) -> str:
        if plan.action_type == FileActionType.CREATE_FOLDER:
            return self._create_folder(plan.destination)
        if plan.action_type == FileActionType.MOVE_FILE:
            return self._move_file(plan.source, plan.destination)
        if plan.action_type == FileActionType.RENAME_FILE:
            return self._rename_file(plan.source, plan.destination)
        if plan.action_type == FileActionType.DELETE_FILE:
            return self._delete_file(plan.source)
        return "[MCP] 未知动作，跳过。"

    def _create_folder(self, path: Path | None) -> str:
        return f"[Function Call Placeholder] create_folder(path='{path}')"

    def _move_file(self, source: Path | None, destination: Path | None) -> str:
        return (
            "[Function Call Placeholder] "
            f"move_file(source='{source}', destination='{destination}')"
        )

    def _rename_file(self, source: Path | None, destination: Path | None) -> str:
        return (
            "[Function Call Placeholder] "
            f"rename_file(source='{source}', destination='{destination}')"
        )

    def _delete_file(self, source: Path | None) -> str:
        return f"[Function Call Placeholder] delete_file(source='{source}')"

