---
name: codegraph
description: Use when exploring an unfamiliar codebase, analyzing call chains, or assessing refactoring impact. Pre-indexed code knowledge graph for AI coding agents — fewer tokens, fewer tool calls, 100% local. Supports Claude Code, Codex, Hermes Agent, Cursor, Gemini, OpenCode, and more via MCP.
tags:
  - code-intelligence
  - MCP
  - knowledge-graph
  - refactoring
  - code-exploration
---

# CodeGraph

**colbymchenry/codegraph** (github.com/colbymchenry/codegraph) — 41.5k ⭐

A pre-indexed code knowledge graph that connects to AI coding agents via MCP (Model Context Protocol). Instead of agents reading/grepping files to understand a codebase, they query the graph instantly — symbol relationships, call graphs, code structure.

## Key Benefits

- ~16% cheaper, ~47% fewer tokens, ~22% faster, ~58% fewer tool calls (benchmarked across 7 languages)
- 100% local — no data leaves your machine
- Works with: Claude Code, Codex, Hermes Agent, Gemini CLI, Cursor, OpenCode, Antigravity, Kiro

## Installation

### Option A: Install script (recommended, no Node.js required)

```bash
curl -fsSL https://raw.githubusercontent.com/colbymchenry/codegraph/main/install.sh | sh
```

Then open a **new terminal** before using.

### Option B: npm (if Node.js already installed)

```bash
npm i -g @colbymchenry/codegraph
```

## Setup for Hermes Agent

### 1. Install the CLI (one of the options above)

### 2. Wire up to agents

```bash
codegraph install          # interactive — picks which agents to configure
codegraph install --yes    # non-interactive — configures all detected agents
```

Detects and auto-configures supported agents (including Hermes Agent) — wires the CodeGraph MCP server into each.

### 3. Verify MCP integration

After `codegraph install --yes`, confirm the MCP server was wired into Hermes:

```bash
grep -A 3 "codegraph" ~/.hermes/config.yaml
# Should show:
#   codegraph:
#     command: codegraph
#     arguments: [serve, --mcp]
```

If that section is missing, re-run `codegraph install --yes` or manually add it to `config.yaml` under `mcp_servers:`:

```yaml
mcp_servers:
  codegraph:
    command: codegraph
    arguments: [serve, --mcp]
```

Then `/reload-mcp` in-session or start a new Hermes session.

### 4. Initialize a project

```bash
cd /path/to/your-project
codegraph init -i
```

`init -i` creates the `.codegraph/` index directory AND builds the initial graph.

On subsequent visits to the same project:

```bash
codegraph index   # rebuild/update the graph
```

## Usage

Once installed + initialized, CodeGraph runs as an MCP server alongside Hermes. When you explore a codebase, Hermes automatically uses `codegraph_explore` tool to query the knowledge graph instead of scanning files with grep/read — fewer tool calls, faster answers.

### Key CLI commands

| Command | Description |
|---------|-------------|
| `codegraph install` | Wire CodeGraph into all supported agents |
| `codegraph init -i` | Init project + build initial index |
| `codegraph index` | Update/reindex current project |
| `codegraph query "how does X work"` | Direct query (without agent) |
| `codegraph status` | Check CodeGraph status |
| `codegraph uninstall` | Remove from all agents |
| `codegraph uninit` | Remove `.codegraph/` from project |

### When to suggest using CodeGraph

- User starts a new project or checks out a repo
- User says "这个项目结构好复杂" / "看不懂代码结构"
- User starts working on an unfamiliar codebase
- Before a major refactoring
- When agent seems to be doing many file reads/greps

## Pitfalls

- **`codegraph install` is interactive by default** — shows a checkbox UI. In non-interactive terminals (background, scripts, agent-terminal), it exits without configuring anything. Always use `codegraph install --yes` in non-interactive contexts.
- **Must run `codegraph install` after installing CLI** — the CLI alone isn't connected to agents.
- **New terminal after install** — the installer puts `codegraph` on PATH but doesn't modify the current shell session. Open a new terminal.
- **`codegraph init` creates `.codegraph/`** — it's a local project directory, commit it or not as preferred.
- **Re-index after major changes** — if the codebase changes significantly, run `codegraph index` to keep the graph current.
- **Only helps structural questions** — for runtime bugs, logic errors, or testing, standard tools still apply.
