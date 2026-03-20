from __future__ import annotations

from localfilemanager.mcp import LocalFileSystemMCP
from localfilemanager.models import FileActionType, PipelineContext, RunMode, UserIntent
from localfilemanager.skills import FileTypeSkill, FolderNamingSkill
from localfilemanager.subagents import (
    ConflictSubAgent,
    FileClassifySubAgent,
    FileScanSubAgent,
    PlanSubAgent,
)


class FileManagerAgent:
    """Agent: orchestrates subagents and execution."""

    def __init__(self) -> None:
        self.scan_subagent = FileScanSubAgent()
        self.classify_subagent = FileClassifySubAgent(FileTypeSkill())
        self.plan_subagent = PlanSubAgent(FolderNamingSkill())
        self.conflict_subagent = ConflictSubAgent()
        self.mcp = LocalFileSystemMCP()

    def run(self, intent: UserIntent) -> PipelineContext:
        context = PipelineContext(intent=intent)
        context.logs.append("[Agent] 收到任务，开始拆解与调度 SubAgent。")

        self.scan_subagent.run(context)
        self.classify_subagent.run(context)
        self.plan_subagent.run(context)
        self.conflict_subagent.run(context)

        context.logs.append("[Agent] 子任务编排结束，进入执行守卫。")
        self._guard_and_execute(context)
        context.logs.append("[Agent] 流程结束。")
        return context

    def _guard_and_execute(self, context: PipelineContext) -> None:
        print("\n=== 计划预览（dry-run）===")
        self._print_plan(context)

        if context.intent.run_mode == RunMode.DRY_RUN:
            confirm = input("\n是否进入真实执行 apply? (yes/no): ").strip().lower()
            if confirm != "yes":
                context.logs.append("[ExecutionGuard] 用户取消，保持 dry-run。")
                return

        for plan in context.plans:
            if plan.action_type == FileActionType.CLASSIFY_ONLY:
                context.logs.append(
                    f"[Executor] 跳过动作（仅分类）: {plan.source} -> {plan.destination}"
                )
                continue
            result = self.mcp.execute(plan)
            context.logs.append(f"[Executor] {result}")

    @staticmethod
    def _print_plan(context: PipelineContext) -> None:
        if not context.plans:
            print("没有可执行计划。")
            return
        for index, plan in enumerate(context.plans, start=1):
            print(
                f"[{index}] action={plan.action_type.value}, "
                f"source={plan.source}, destination={plan.destination}, reason={plan.reason}"
            )

