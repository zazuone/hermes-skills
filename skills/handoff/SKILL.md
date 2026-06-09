---
name: handoff
description: Compact the current conversation into a structured handoff document so another agent session can continue the work. Includes context, decisions made, remaining work, and suggested skills. Use when ending a session that others will continue, before delegate_task calls, or when the user says "handoff", "write a handoff", "summarize for next session".
triggers:
  - handoff
  - write handoff
  - session summary
  - continue later
---

# Handoff

Compact the current conversation into a handoff document that a fresh agent can pick up and continue without asking redundant questions.

## Output format

Write to `.hermes/handoffs/{topic}-{timestamp}.md`

```markdown
# Handoff: {topic}

## Context
[What were we working on? 2-3 sentences max. Link to relevant files/issues.]

## Active State
- Current branch / commit: 
- Key files being modified: 
- Running processes (if any): 

## Decisions Made
- [decision 1 with reasoning]
- [decision 2 with reasoning]

## Remaining Work
- [ ] Task 1 (next priority)
- [ ] Task 2
- [ ] Task 3

## Blockers
[Anything blocking progress]

## Suggested Skills
- [`skill-name`](skill:skill-name) — why this skill would help continue

## Key Context
[Critical details, file paths, API keys (redacted), environment info]
```

## Rules

1. **Don't duplicate artifacts** — if decisions are already captured in plans, ADRs, commits, or issues, reference them by path instead of repeating.
2. **Redact secrets** — API keys, passwords, tokens, PII.
3. **Link, don't copy** — reference file paths, commit hashes, URLs rather than dumping content.
4. **Tailor to the next agent** — if you know what the next session will do, focus the handoff on that.
5. **Keep it under 100 lines** — handoffs should be quick to read.
