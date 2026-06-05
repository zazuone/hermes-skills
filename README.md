# Hermes Skills

My custom Hermes Agent skills — shareable across machines via `hermes skills tap`.

## Skills

| Skill | Description |
|-------|-------------|
| **tdd-pro** | Orchestrated TDD workflow — RED-GREEN-REFACTOR + CodeGraph code intelligence + ocr review |
| **open-code-review** | Use Alibaba's open-code-review (ocr) CLI for AI-powered code review |
| **codegraph** | Pre-indexed code knowledge graph for AI coding agents via MCP |

## Usage

```bash
# Add this repo as a tap source (one-time)
hermes skills tap add zazuone/hermes-skills

# Install a skill
hermes skills install tdd-pro
hermes skills install open-code-review
hermes skills install codegraph

# Or install by full identifier
hermes skills install zazuone/hermes-skills/skills/tdd-pro
```

Then start Hermes with:

```bash
hermes --skills tdd-pro,open-code-review,codegraph
```

Or load in-session:

```
/skill tdd-pro
/skill open-code-review
/skill codegraph
```
