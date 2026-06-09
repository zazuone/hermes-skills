---
name: open-code-review
description: Use before opening a PR, after large changesets, or when user asks "帮我 review". Alibaba open-code-review (ocr) CLI for AI-powered code review — supports workspace, branch diff, and single commit review.
tags:
  - code-review
  - github
  - PR
  - review
---

# Open Code Review (ocr)

Use **Alibaba Open Code Review** (`ocr`) to get AI-powered, line-level code review on your diffs. It uses a hybrid deterministic+LLM architecture, already configured to use `deepseek-v4-flash` model via the local ccx-go proxy.

## Prerequisites

- `ocr` binary installed at `/usr/local/bin/ocr` (version: open-code-review v1.1.18)
- LLM configured at `~/.opencodereview/config.json`:
  - URL: `http://localhost:3688/v1`
  - Model: `deepseek-v4-flash`
  - Auth: ccx-go PROXY_ACCESS_KEY
- Project must be a Git repository

## When to Use

Trigger conditions:
- User asks "审查代码" / "帮我 review 一下" / "code review"
- Before opening a PR or merging a branch
- After making changes to multiple files
- When user reports a bug that might have been caught by review

## Commands

### Quick start — review workspace changes

```bash
cd /path/to/project
ocr review
```

Reviews all staged, unstaged, and untracked changes in the working tree.

### Branch diff review

```bash
ocr review --from main --to feature-branch
```

### Single commit

```bash
ocr review --commit <commit-sha>
```

### Full help

```bash
ocr --help
ocr review --help
```

## Output Interpretation

The tool outputs structured review comments with:
- **File path** and line numbers — what file and where
- **Severity** — issue importance level
- **Suggestion** — concrete code improvement recommendation

Example output typically includes:
- Potential bugs (NPE, thread-safety, SQL injection, XSS)
- Code style issues
- Logic errors
- Security concerns

## Tips

- For large changesets, `ocr review` uses divide-and-conquer (splits files into bundles, each reviewed by a sub-agent) — it handles big PRs better than general-purpose agents.
- The built-in rule set includes NPE, thread-safety, XSS, and SQL injection patterns.
- You can tweak the model or add `llm.extra_body` in the config if needed.
- If you get 401 errors, the PROXY_ACCESS_KEY may have changed — check `/home/zazuone/Desktop/00code/ccx/backend-go/.env`.

## Pitfalls

- **Must be in a git repo** — ocr reads git diffs. Running it outside a git repo will fail.
- **No uncommitted changes in branch mode** — when using `--from`/`--to`, make sure the branches exist and are up to date.
- **LLM must be running** — depends on ccx-go on port 3688. If it's down, `ocr llm test` will fail.
- **Performance on huge PRs** — very large diff sets (>50 files) take longer but are handled via the bundled sub-agent approach.
- **`ocr config set` masks auth tokens** — the `ocr config set llm.auth_token` command writes `***` to config.json instead of the actual key. Always write the config file directly (use `write_file` or `cat > ~/.opencodereview/config.json`) to get the real token stored.
- **All three env vars required** — `OCR_LLM_URL`, `OCR_LLM_MODEL`, and `OCR_LLM_TOKEN` must all be set together. The tool refuses to start if `OCR_LLM_TOKEN` is missing, even for non-Anthropic (OpenAI-compatible) endpoints.
- **npm install may timeout** — the npm postinstall script downloads a binary from GitHub releases. On slow connections, use direct binary download instead: `curl -L -o /tmp/ocr <release-url> && chmod +x /tmp/ocr && sudo mv /tmp/ocr /usr/local/bin/ocr`.
