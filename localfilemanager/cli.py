from __future__ import annotations

from pathlib import Path

from localfilemanager.agent import FileManagerAgent
from localfilemanager.models import RunMode, UserIntent


def run_cli() -> None:
    print("=== LocalFileManager V1 (无代码学习版) ===")
    print("目标：观察 Agent 拆任务与 SubAgent 协作。")
    print("默认策略：保守模式 dry-run + 冲突逐条询问。")

    raw = input("\n请输入目标指令(示例: 帮我按文件类型整理文件夹): ").strip()
    target = input("请输入目标文件夹路径: ").strip()

    intent = UserIntent(
        raw_text=raw or "帮我按文件类型整理文件夹",
        target_path=Path(target),
        run_mode=RunMode.DRY_RUN,
    )
    agent = FileManagerAgent()
    context = agent.run(intent)

    print("\n=== 运行日志（学习观察）===")
    for line in context.logs:
        print(line)

