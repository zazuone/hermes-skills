# Hermes Skills

My custom Hermes Agent skills — shareable across machines via `hermes skills tap`.

## Skills

| Skill | When to Use | What It Does |
|-------|------------|-------------|
| **tdd-pro** | New features, bug fixes, refactoring | TDD + CodeGraph + ocr review orchestration |
| **codegraph** | Exploring unfamiliar code, refactoring | Pre-indexed code knowledge graph via MCP |
| **open-code-review** | Before PR, after changes, "帮我 review" | Alibaba ocr CLI for AI-powered code review |
| **feishu-doc** | 飞书文档 / feishu doc / lark doc | Create, read, populate Feishu docs via API |
| **task-file-automation** | 每日任务 / task auto / cron任务 | Nightly cron from Feishu → execute → log |
| **grill-me** | "Grill me", "stress test" this plan | Interview relentlessly before committing |
| **handoff** | "Handoff", session summary for next agent | Structured session-to-session handoff doc |
| **caveman** | "Caveman mode", "be brief", 省 token | Ultra-compressed responses |

## Usage

```bash
# Add this repo as a tap source (one-time)
hermes skills tap add zazuone/hermes-skills

# Install skills
hermes skills install tdd-pro codegraph open-code-review
hermes skills install grill-me handoff caveman
hermes skills install feishu-doc task-file-automation

# Or install by full identifier
hermes skills install zazuone/hermes-skills/skills/tdd-pro
```

Then load in-session:

```
/skill tdd-pro
/skill codegraph
/skill open-code-review
/skill grill-me
```

## Contributing

See [CLAUDE.md](./CLAUDE.md) — the agent self-maintenance guide.
