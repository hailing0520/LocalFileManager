# LocalFileManager (V1 学习版)

这是一个面向初学者的智能体架构演示项目，重点不是“立刻自动化整理文件”，而是先理解以下原理：

- Agent 如何拆任务
- SubAgent 如何协作
- Skill 如何驱动决策
- MCP 如何承接外部系统
- Function Call 如何落地执行（V1 用占位符模拟）

## 1. 项目目标

首个目标指令（可扩展）：

- `帮我按文件类型整理文件夹`

V1 支持的能力范围：

- 只分类（不动文件）
- 移动文件（占位执行）
- 重命名文件（占位执行）
- 删除文件（占位执行）
- 创建文件夹（占位执行）

安全策略（默认）：

- 保守模式：`dry-run`
- 所有真实执行都要求确认
- 同名冲突：每次都询问用户

## 2. 目录结构

```text
LocalFileManager/
├─ main.py
├─ pyproject.toml
├─ README.md
└─ localfilemanager/
   ├─ __init__.py
   ├─ cli.py
   ├─ models.py
   ├─ skills.py
   ├─ subagents.py
   ├─ agent.py
   └─ mcp.py
```

## 3. 架构映射（核心）

### Agent（总控）

- 文件：`localfilemanager/agent.py`
- 职责：接收 `UserIntent`，编排 SubAgent，控制 `dry-run -> apply` 守卫，汇总日志。

### SubAgent（分区）

- 文件：`localfilemanager/subagents.py`
- `FileScanSubAgent`：扫描文件
- `FileClassifySubAgent`：使用 Skill 分类
- `PlanSubAgent`：生成动作计划
- `ConflictSubAgent`：发现同名冲突并逐条询问用户

### Skill（知识/手艺）

- 文件：`localfilemanager/skills.py`
- `FileTypeSkill`：扩展名 -> 分类目录
- `FolderNamingSkill`：分类 -> 目标文件夹

### MCP（标准接口）

- 文件：`localfilemanager/mcp.py`
- `LocalFileSystemMCP`：承接动作请求并调用 Function Call（当前为占位符输出）

### Function Call（底层动作）

当前使用占位符模拟并打印以下动作：

- `create_folder(path)`
- `move_file(source, destination)`
- `rename_file(source, destination)`
- `delete_file(source)`

> 说明：V1 故意不用真实写盘操作，确保你先看懂调用链。

## 4. 运行方式

在项目根目录执行：

```bash
python main.py
```

运行后将提示你输入：

1. 自然语言指令
2. 目标文件夹路径

然后会执行完整流程：

1. Agent 接收任务
2. SubAgent 扫描
3. SubAgent 分类
4. SubAgent 计划
5. SubAgent 冲突处理（逐条问询）
6. ExecutionGuard 显示 dry-run 计划
7. 用户确认后才执行占位动作
8. 输出全量日志（用于学习）

## 5. 你能观察到什么（学习重点）

### A. Agent 拆任务

看日志中这几段：

- `[Agent] 收到任务，开始拆解与调度 SubAgent。`
- `[Agent] 子任务编排结束，进入执行守卫。`

你会看到：Agent 本身不做细节动作，而是负责“编排和总控”。

### B. SubAgent 协作

看日志顺序：

- `FileScan` -> `FileClassify` -> `Plan` -> `Conflict`

你会看到：每个 SubAgent 只干一件事，上游输出直接喂给下游。

### C. Skill 驱动决策

分类行为由 `FileTypeSkill` 决定，不写死在 Agent 中。

### D. MCP 与 Function Call

执行阶段会打印：

- `[Function Call Placeholder] ...`

这表示：MCP 已经接到任务并映射到底层动作，只是 V1 暂不真实落盘。

## 6. 关键交互说明

### 6.1 dry-run 守卫

默认先显示计划，不会直接执行。只有输入 `yes` 才进入 apply。

### 6.2 同名冲突策略

发现冲突后，逐条询问：

- `1) 跳过`
- `2) 自动重命名`
- `3) 覆盖`

### 6.3 占位执行

即便进入 apply，V1 仍会打印占位 Function Call，避免误操作真实文件。

## 7. 已知限制（V1）

- 不递归扫描子目录（仅当前目录）
- 不进行真实文件操作（故意设计）
- 冲突处理只做基础分支演示
- 暂无持久化日志文件

## 8. 推荐下一步（V2 方向）

当你确认 V1 原理已掌握，可以按顺序升级：

1. 将 `mcp.py` 的占位动作替换为真实文件操作
2. 增加“先备份再执行”策略
3. 增加递归扫描与过滤规则（忽略隐藏文件等）
4. 将日志写入 `logs/` 目录做审计追踪
5. 为每个 SubAgent 增加单元测试

## 9. 快速排错

- 如果提示路径无效：确认输入的是存在且可访问的目录
- 如果没有发现文件：目标目录可能为空或全是子目录
- 如果流程中断：检查交互输入是否为空或非法（尤其冲突选项）

---

如果你需要，我可以继续在 V1 基础上帮你做一个 **V1.1（仍保守）**：

- 增加递归扫描
- 增加“只分类不执行”开关
- 增加日志落盘
- 保持默认 dry-run，不改变安全策略