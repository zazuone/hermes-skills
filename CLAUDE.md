# Hermes Skills — Maintenance Guide

This repository is a **GitHub tap repo** for Hermes Agent skills. Skills here are shared across machines via `hermes skills tap add zazuone/hermes-skills`.

## Directory Structure

```
hermes-skills/
├── CLAUDE.md              ← this file — tells agents how to maintain this repo
├── README.md              ← overview for human visitors on GitHub
└── skills/
    ├── <skill-name>/
    │   ├── SKILL.md       ← required: the skill definition
    │   ├── references/    ← optional: deep reference docs
    │   └── templates/     ← optional: reusable templates
    └── ...
```

Each skill lives in its own directory under `skills/`. No subcategories needed — Hermes uses the skill's `category:` frontmatter field for grouping.

## How to Add a New Skill

1. **Check if it already exists** — `ls skills/` and skim peer SKILL.md files
2. **Create directory** — `skills/<name>/`
3. **Write SKILL.md** — follow the format below
4. **Add to git** — `git add skills/<name>/ && git commit`
5. **Push** — `git push`

## SKILL.md Format

Every skill must have a `skills/<name>/SKILL.md` file with YAML frontmatter:

```yaml
---
name: my-skill
description: Use when <trigger>. <one-line behavior>.
category: productivity     # or: devops, mlops, research, creative, etc.
triggers:
  - "user says this"
  - "context matches that"
---
```

**Rules:**
- Name: lowercase, hyphens, ≤ 64 chars
- Description: ≤ 1024 chars, starts with "Use when..."
- Must have a non-empty body after the closing `---`

**Good description examples:**
- `Use when reviewing a PR or workspace changes. Alibaba ocr CLI for AI-powered code review.`
- `Use when exploring an unfamiliar codebase or assessing refactoring impact. Code intelligence via MCP.`

## How to Update an Existing Skill

1. **Fix frontmatter** — `description` and `triggers` in the YAML frontmatter (lines 1-9)
2. **Fix body** — update the markdown body below the closing `---`
3. **When to version-bump:** the `version` field is optional. Bump it when the changes break backward compatibility (changed commands, removed features). Don't bump for minor improvements or bug fixes.

## Naming Convention

Skills describe **classes of problems**, not single tasks.

| ✅ Good | ❌ Bad |
|---------|--------|
| `feishu-doc` | `create-feishu-doc-abc123` |
| `open-code-review` | `review-pr-42` |
| `task-file-automation` | `feishu-task-tool-v2` |

If a name only makes sense for today's session, it's too narrow. Step back and name the problem class.

## When to Create vs. Update vs. Delete

| Action | When |
|--------|------|
| **Create** | New problem class not covered by existing skills |
| **Patch** | Add steps, fix commands, document pitfalls |
| **Merge into umbrella + delete** | Skill is too narrow; its content fits into a broader skill |
| **Delete with forwarding** | Skill content merged into umbrella — set `absorbed_into=<umbrella>` |
| **Delete (prune)** | Skill is truly stale, never used — set `absorbed_into=""` |

## Quality Checklist

Before committing, verify:
- [ ] SKILL.md has valid frontmatter (`---` at byte 0)
- [ ] Description is a trigger-first "Use when..." sentence
- [ ] Triggers listed in frontmatter `triggers:` array
- [ ] Body has at minimum: Overview + When to Use + Common Pitfalls
- [ ] No sensitive info (API keys, passwords, tokens)
- [ ] Commands are tested and work on the target platform
- [ ] `references/` dir used for deep docs >15k chars

## Deployment

Push to GitHub → consumers run `hermes skills check && hermes skills update` to pick up changes.
