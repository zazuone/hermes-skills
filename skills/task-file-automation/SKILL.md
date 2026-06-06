---
name: task-file-automation
description: 每日任务文件 cron job — 读取 C:\Users\hello\Desktop\任务.md，解析三栏，执行待办任务，更新文件状态
category: productivity
triggers:
  - "任务.md"
  - "每日任务"
  - "task auto"
  - "任务自动化"
---

# 任务文件自动化

## 架构

```
任务.md (三栏: ## 待完成任务 / ## 当前进度 / ## 已完成)
    │
    ▼  cron: 0 0 * * *
 Hermes Agent Session
    │
    ├─ 读取文件 → 解析三栏
    ├─ 优先检查「当前进度」恢复中断
    ├─ 无中断则从「待完成」取第一条
    ├─ 用 Agent tools 执行任务内容
    ├─ 更新文件: 移栏 + 时间戳 + 备注
    └─ 循环到清空或 8:00
## 📄 2026-06-06 更新：已迁移到飞书文档

本地 `任务.md` 已废弃。改为两个飞书文档：

- **📋 每日任务日志**（写待办）: `Vua7d1EhOoDipqxwV4ocZUKJnMf`
- **🗃 任务自动化 — 执行日志**（记录详情）: `IMWodguGDoboILxP1wUc6hhlngd`

### 文档结构（用户端）

```
每日任务日志:
  ## 📋 待完成任务
    - 用户在这里写待办事项
  ## ➡️ 当前进度
    - 执行中/中断的任务
  ## ✅ 已完成
    - 已完成的任务（时间戳）

执行日志:
  ## 📖 执行记录
    - ⏱ 时间
       【原记录】用户写的原文
       【执行方案】怎么干的
       【执行结果】最终结果
       【待完成】还差什么
```

### 工具脚本

`~/.hermes/scripts/feishu_task_tool.py`
- `read_tasks` → JSON 输出三栏任务
- `append_log <原> <方案> <结果> <待完成>` → 追加执行记录
- `update_tasks [pending] [progress] [completed]` → 更新三个章节
```

## 关键规则

1. **时间窗口**: 0:00~8:00，超时中断，任务留在「当前进度」
2. **错误处理**: 失败 → 移到已完成 + `[失败: 原因]`，继续下一条
3. **恢复机制**: 每次启动先检查「当前进度」，有中断任务则优先续上
4. **格式**: 已完成 `- 任务名 (YYYY-MM-DD HH:MM)`，备注 `[备注]`

## 测试库

`~/.hermes/scripts/task_manager.py` — 纯函数库，16 个 TDD 测试：

| 函数 | 用途 | 测试数 |
|:--|:--|:--:|
| `parse_task_file(text)` | 解析三栏 markdown | 4 |
| `format_task_file(data)` | 序列化回 markdown | 2 |
| `move_task(data, task, from, to)` | 栏间移动 | 4 |
| `format_completed(name, ts, notes)` | 已完成行格式 | 2 |
| `format_progress(name, step)` | 进度行格式 | 1 |
| `should_stop(hour, max=8)` | 执行窗口判断 | 3 |

## 常用命令

```bash
# 手动触发验收
cronjob action=run job_id=<id>

# 查看最近一次执行
cronjob action=list

# 更新提示词
cronjob action=update job_id=<id> prompt="..."
```

## 参考文件

- `references/cron-security-workaround.md` — 完整错误信息、替代工具表和配置方法
- `references/large-task-execution.md` — 跨上下文压缩的大规模任务执行策略
- `references/feishu-dispatch.md` — 将任务执行结果推送到飞书文档的消息格式和 API 模式

## 陷阱 / 注意事项

- 文件路径跨 WSL: Windows `C:\` → WSL `/mnt/c/`
- cron job 的 prompt 必须**自包含**（不能 ask the user）
- 任务语义可能模糊 — 需要 agent 自行推断
- 长时间任务（如下载大文件）可能被 8:00 窗口打断
- 时间戳的 `??:??`：如果 `approvals.cron_mode` 未开放 terminal，精确时间无法获取，时间戳会显示 `(2026-06-04 ??:??)` — 如实保留，不要捏造
- `approvals.cron_mode: approve` 是必须步骤，否则 cron 内所有 terminal/execute_code 失败

### ⚠️ 必要配置：`approvals.cron_mode: approve`

cron job 默认以 `deny` 策略运行，阻止所有 shell 和 Python 执行。**必须在设置 cron job 后修改配置**：

```bash
hermes config set approvals.cron_mode approve
```

否则 `terminal` 会报 `"Security scan: security issue detected"`，`execute_code` 报 `"Cron jobs run without a user present to approve it"`。

### 替代方案（当无法改配置时）

| 受阻操作 | 替代方案 |
|:--|:--|
| `ls`, `cat`, `which` | 不使用 terminal — 用 file 工具 |
| `echo > file` | `write_file(path, content)` |
| `ls /dir/` | `search_files(target='files', pattern='*', path='/dir/')` |
| 获取时间 | conversation 元数据有 `Conversation started: ...`；或用 write_file 写入估算 |
| Python 逻辑 | 无法绕过 — 需要终端或 config 信任 |

### 真实运行验证 (2026-06-04)

手动触发 `cronjob(action='run')`，三条小任务验证通过：

1. 写入字符串到 test_result_1.txt → ✅ 内容正确
2. 列出 scripts 目录到 test_result_2.txt → ✅ 目录结构完整
3. 写入系统时间到 test_result_3.txt → ✅ 有时间信息，注明 terminal 受限

文件更新自动完成：三条任务从「待完成」→「当前进度」→「已完成」，每条带时间戳和备注。
