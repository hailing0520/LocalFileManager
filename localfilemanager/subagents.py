from __future__ import annotations

from pathlib import Path

from localfilemanager.models import (
    ActionPlanItem,
    FileActionType,
    FileItem,
    PipelineContext,
)
from localfilemanager.skills import FileTypeSkill, FolderNamingSkill


class FileScanSubAgent:
    def run(self, context: PipelineContext) -> None:
        base = context.intent.target_path
        context.logs.append(f"[SubAgent-FileScan] 扫描目录: {base}")
        if not base.exists() or not base.is_dir():
            context.logs.append("[SubAgent-FileScan] 目录不存在或不可用。")
            return

        for child in base.iterdir():
            if child.is_file():
                context.files.append(FileItem(path=child, extension=child.suffix.lower()))
        context.logs.append(f"[SubAgent-FileScan] 扫描完成，共发现文件 {len(context.files)} 个。")


class FileClassifySubAgent:
    def __init__(self, type_skill: FileTypeSkill) -> None:
        self.type_skill = type_skill

    def run(self, context: PipelineContext) -> None:
        context.logs.append("[SubAgent-FileClassify] 开始按类型分类（Skill 驱动）。")
        for item in context.files:
            item.category = self.type_skill.classify(item.path)
            context.logs.append(
                f"[SubAgent-FileClassify] {item.path.name} -> {item.category}"
            )


class PlanSubAgent:
    def __init__(self, folder_skill: FolderNamingSkill) -> None:
        self.folder_skill = folder_skill

    def run(self, context: PipelineContext) -> None:
        context.logs.append("[SubAgent-Plan] 生成动作计划。")
        base = context.intent.target_path
        created_folders: set[Path] = set()

        for item in context.files:
            target_folder = self.folder_skill.target_folder(base, item.category)
            if target_folder not in created_folders:
                context.plans.append(
                    ActionPlanItem(
                        action_type=FileActionType.CREATE_FOLDER,
                        destination=target_folder,
                        reason="分类目录准备",
                    )
                )
                created_folders.add(target_folder)

            target_file = target_folder / item.path.name
            context.plans.append(
                ActionPlanItem(
                    action_type=FileActionType.MOVE_FILE,
                    source=item.path,
                    destination=target_file,
                    reason=f"按类型归档到 {item.category}",
                )
            )
        context.logs.append(f"[SubAgent-Plan] 计划生成完成，共 {len(context.plans)} 条。")


class ConflictSubAgent:
    def run(self, context: PipelineContext) -> None:
        context.logs.append("[SubAgent-Conflict] 检查同名冲突（策略：每次询问用户）。")
        for plan in context.plans:
            if plan.action_type != FileActionType.MOVE_FILE:
                continue
            if plan.destination and plan.destination.exists():
                context.logs.append(
                    f"[SubAgent-Conflict] 检测到冲突: {plan.destination.name}"
                )
                decision = self._ask_user(plan.destination.name)
                context.logs.append(f"[SubAgent-Conflict] 用户选择: {decision}")
                if decision == "1":
                    plan.action_type = FileActionType.CLASSIFY_ONLY
                    plan.reason += "；因冲突跳过移动"
                elif decision == "2" and plan.destination:
                    plan.action_type = FileActionType.RENAME_FILE
                    plan.destination = self._next_name(plan.destination)
                    plan.reason += "；冲突后改名"
                elif decision == "3":
                    plan.reason += "；确认覆盖（占位）"
                else:
                    plan.action_type = FileActionType.CLASSIFY_ONLY
                    plan.reason += "；无效输入，默认跳过"

    @staticmethod
    def _ask_user(filename: str) -> str:
        print(f"\n[冲突询问] 目标文件已存在: {filename}")
        print("1) 跳过  2) 自动重命名  3) 覆盖")
        return input("请选择处理方式(1/2/3): ").strip()

    @staticmethod
    def _next_name(path: Path) -> Path:
        return path.with_name(f"{path.stem}_renamed{path.suffix}")

