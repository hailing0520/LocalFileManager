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

## 4. 模型 / Agent / MCP / Tool 权限边界

这张表用于明确“谁能做什么、谁不能做什么、出了问题谁负责”。

| 组件 | 核心职责 | 有哪些权限 | 明确没有的权限 | 输入 | 输出 | 失败责任归属 |
|---|---|---|---|---|---|---|
| 模型（LLM） | 理解指令、推理、生成计划、生成 Function Call 请求 | 生成结构化调用请求；基于上下文决策；汇总结果 | 不能直接访问本地文件/数据库/网络；不能直接执行系统命令 | 用户意图、上下文、工具描述、历史结果 | 文本答复 / JSON / Function Call 请求 | 参数不合理、推理偏差由模型侧负责 |
| Agent（编排层） | 任务拆解、流程控制、状态管理、安全守卫 | 决定是否调用工具；组织调用顺序；做人机确认门禁 | 不应直接承载底层外部系统细节（应下沉 MCP/Tool） | 用户请求、模型输出、运行状态 | 执行计划、调用请求、最终汇总 | 编排错误、流程遗漏由 Agent 负责 |
| MCP（协议/适配层） | 统一外部能力接口，做参数映射与标准化返回 | 参数校验、能力适配、错误归一化 | 不应做高层业务决策（例如“要不要删除文件”） | Agent 的调用意图 | 标准化执行结果（success/data/error） | 协议映射错误、适配不一致由 MCP 负责 |
| Tool（执行层） | 执行最小原子动作（读写文件、移动、删除等） | 真实访问外部资源并返回执行结果 | 不应负责全局规划与复杂业务策略 | MCP/Agent 下发的动作参数 | 原子执行结果（成功/失败/错误详情） | 资源不可用、执行失败由 Tool 负责 |

### 4.1 在本项目中的对应关系

- 模型（LLM）：当前 V1 以规则和流程模拟，后续可接入真实大模型
- Agent：`localfilemanager/agent.py`
- MCP：`localfilemanager/mcp.py` 中的 `LocalFileSystemMCP`
- Tool：`LocalFileSystemMCP` 内部 `_create_folder/_move_file/_rename_file/_delete_file`

### 4.2 错误归因流程（文本版）

1. 如果是“删不删、先做什么后做什么”决策错误，先看 Agent/策略。
2. 如果是“工具参数映射错、返回结构混乱”，先看 MCP 适配层。
3. 如果是“路径权限不足、文件被占用、磁盘问题”，先看 Tool 执行层。
4. 如果是“调用请求参数本身不合理”，回溯模型输出或上游约束。

## 5. 运行方式

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

## 6. 你能观察到什么（学习重点）

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

## 7. 关键交互说明

### 6.1 dry-run 守卫

默认先显示计划，不会直接执行。只有输入 `yes` 才进入 apply。

### 6.2 同名冲突策略

发现冲突后，逐条询问：

- `1) 跳过`
- `2) 自动重命名`
- `3) 覆盖`

### 6.3 占位执行

即便进入 apply，V1 仍会打印占位 Function Call，避免误操作真实文件。

## 8. 已知限制（V1）

- 不递归扫描子目录（仅当前目录）
- 不进行真实文件操作（故意设计）
- 冲突处理只做基础分支演示
- 暂无持久化日志文件

## 9. 推荐下一步（V2 方向）

当你确认 V1 原理已掌握，可以按顺序升级：

1. 将 `mcp.py` 的占位动作替换为真实文件操作
2. 增加“先备份再执行”策略
3. 增加递归扫描与过滤规则（忽略隐藏文件等）
4. 将日志写入 `logs/` 目录做审计追踪
5. 为每个 SubAgent 增加单元测试

## 10. 快速排错

- 如果提示路径无效：确认输入的是存在且可访问的目录
- 如果没有发现文件：目标目录可能为空或全是子目录
- 如果流程中断：检查交互输入是否为空或非法（尤其冲突选项）

---

如果你需要，我可以继续在 V1 基础上帮你做一个 **V1.1（仍保守）**：

- 增加递归扫描
- 增加“只分类不执行”开关
- 增加日志落盘
- 保持默认 dry-run，不改变安全策略