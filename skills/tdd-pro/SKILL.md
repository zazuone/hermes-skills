---
name: tdd-pro
description: Use when developing new features, fixing bugs, or doing major refactoring. Orchestrated TDD workflow — RED-GREEN-REFACTOR augmented with CodeGraph code intelligence and open-code-review (ocr) quality gates. Fewer tokens, fewer bugs, cleaner code.
tags:
  - tdd
  - code-review
  - code-intelligence
  - workflow
related_skills:
  - test-driven-development
  - codegraph
  - open-code-review
---

# TDD Pro

**TDD + CodeGraph + open-code-review** 三合一编排工作流。

在经典 RED-GREEN-REFACTOR 循环的关键节点，插入 CodeGraph 代码探索和 ocr 代码审查，让每个阶段更高效、更安全。

## 依赖

此 skill 要求以下技能已加载：
- `test-driven-development` — TDD 核心规则（铁律、RED-GREEN-REFACTOR、反模式）
- `codegraph` — 预建代码知识图谱（代码探索、调用分析）
- `open-code-review` — AI 代码审查（行级 review、安全/质量检测）

### 安装方式

**方式 A：从 GitHub tap 安装（推荐，多机同步）**
```bash
hermes skills tap add zazuone/hermes-skills
hermes skills install tdd-pro
# tdd-pro 会自动拉取依赖的 codegraph 和 open-code-review
```

**方式 B：启动时加载**
```bash
hermes --skills test-driven-development,codegraph,open-code-review
```

**方式 C：在 session 中加载**
```
/skill test-driven-development
/skill codegraph
/skill open-code-review
```

## 集成工作流

```
┌─────────────────────────────────────────────────────────┐
│  TDD Pro 循环                                            │
│                                                         │
│  RED ──── CodeGraph ──── 写测试 ──── 验证失败            │
│           ① 理解结构     ② 精准测试                       │
│                                                         │
│  GREEN ── CodeGraph ──── 实现 ──── ocr review ── 绿      │
│           ③ 导航代码     ④ 编码    ⑤ 质量门禁             │
│                                                         │
│  REFACTOR  CodeGraph ──── 重构 ──── ocr review ── 绿     │
│           ⑥ 影响分析     ⑦ 清理    ⑧ 二次审查             │
│                                                         │
│  → 回到 RED (下一个行为)                                  │
└─────────────────────────────────────────────────────────┘
```

### ① RED 阶段 — 写测试前：CodeGraph 代码探索

任务是写一个测试？先让 CodeGraph 摸清结构：

```bash
# 找某个函数的调用者 — 理解接口契约
codegraph callers "ClassName.method_name"

# 找某个函数的内部调用 — 理解依赖关系
codegraph callees "ClassName.method_name"

# 自由搜索符号
codegraph query "parameter validation"
codegraph query "energy dispatch interface"

# 查看文件结构
codegraph files
```

**目的**：不靠 grep 扫文件，直接拿到符号关系和调用链，写出更精准的测试。

### ② RED 阶段 — 写测试

严格遵循 `test-driven-development` 的铁律：
1. 写一个最小测试，描述期望行为
2. 用 `pytest` 跑，验证它确实失败（RED 确认）
3. 失败的 reason 必须是"功能缺失"，不是"代码写错"

### ③ GREEN 阶段 — 实现前：CodeGraph 导航

开始写实现前，用 CodeGraph 找到代码的正确位置：

```bash
# 确认要改的符号位置
codegraph query "target_function"

# 分析改动影响面
codegraph impact "ClassName.method_name"

# 查看项目文件布局
codegraph files
```

### ④ GREEN 阶段 — 最小实现

写刚好能让测试通过的最简代码。允许任何"作弊"手段：
- 硬编码返回值
- 复制粘贴
- 不处理边界

**这阶段不优化，只求通过。**

### ⑤ GREEN 阶段 — 质量门禁：ocr review

测试通过后、提交前，跑一次代码审查：

```bash
# 审查当前所有改动
ocr review

# 或只审查某个 commit
ocr review --commit HEAD
```

**ocr 会检查：**
- 潜在的 NPE / 线程安全问题
- SQL 注入 / XSS 风险
- 代码风格问题
- 逻辑错误

**如果 ocr 报出问题：**
1. 修复问题
2. 重新确认测试仍通过
3. 再跑一次 `ocr review` 确认已解决

### ⑥ REFACTOR 阶段 — 重构前：CodeGraph 影响分析

重构之前，先搞清楚改动会波及哪些地方：

```bash
# 分析修改某个符号的影响范围
codegraph impact "ClassName.field_or_method"

# 找受影响的测试文件
codegraph affected src/changed_file.py

# 确认调用链
codegraph callers "refactored_function"
```

### ⑦ REFACTOR 阶段 — 清理代码

在测试全绿的前提下重构：
- 消除重复
- 改善命名
- 提取辅助函数
- 简化表达式

**每步都跑测试，绿了再走下一步。**

### ⑧ REFACTOR 阶段 — 二次审查：ocr review

重构完成后，再来一轮审查确认重构没引入新问题：

```bash
ocr review
```

**对比第一次 ocr 输出** — 应该看到更少的警告（说明重构有效）。

### → 回到 RED

进入下一个 TDD 循环，为下一个行为写测试。

## 快速命令速查

| 阶段 | 命令 | 做什么 |
|------|------|--------|
| RED | `codegraph callers/callees/query` | 理解代码结构 |
| GREEN | `codegraph query/files` | 导航到实现位置 |
| GREEN→ | `ocr review` | 检查实现质量 |
| REFACTOR | `codegraph impact/affected` | 分析波及范围 |
| REFACTOR→ | `ocr review` | 检查重构质量 |
| 全程 | `pytest tests/ -q` | 验证测试全绿 |

## 何时使用

- **新功能开发** — 完整的 RED-GREEN-REFACTOR 循环
- **修复 bug** — 先写复现测试，再修复，最后审查
- **大规模重构** — 用 CodeGraph 分析影响 + ocr 验证结果
- **代码 review 前** — 自己先用 ocr 过一遍再提 PR

## 何时跳过某些步骤

- **纯探索/原型** — 跳过 ocr review（但仍建议用 CodeGraph 导航）
- **配置/生成代码** — 跳过 TDD 和 ocr
- **微小改动（1-2 行）** — 跳过 ocr，保留 TDD + CodeGraph
- **CodeGraph 未建索引** — `codegraph init -i` 初始化后仍可用 fallback 到 grep

## 反模式

- ❌ 只 ocr review 不跑测试 — 错过功能验证
- ❌ 只跑测试不 ocr review — 错过静态分析和安全检测
- ❌ 重构时不跑 `codegraph impact` — 改出连锁 bug 不自知
- ❌ 一次改太多再 ocr review — 反馈太慢，建议每步小改小查
- ❌ 跳过 RED 直接写代码再用 ocr 补查 — 这是测试后的 review，不是 TDD
