from __future__ import annotations

from pathlib import Path


class FileTypeSkill:
    """Skill: map extension to category."""

    _EXT_MAP = {
        ".jpg": "images",
        ".jpeg": "images",
        ".png": "images",
        ".gif": "images",
        ".pdf": "documents",
        ".doc": "documents",
        ".docx": "documents",
        ".txt": "documents",
        ".zip": "archives",
        ".rar": "archives",
        ".7z": "archives",
        ".py": "code",
        ".js": "code",
        ".ts": "code",
        ".json": "code",
    }

    def classify(self, file_path: Path) -> str:
        return self._EXT_MAP.get(file_path.suffix.lower(), "others")


class FolderNamingSkill:
    """Skill: build destination folder by category."""

    def target_folder(self, base_path: Path, category: str) -> Path:
        return base_path / category

