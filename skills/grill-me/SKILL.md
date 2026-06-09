---
name: grill-me
description: Interview the user relentlessly about a plan or design until reaching shared understanding. Resolves branches of the decision tree one by one. Use when user says "grill me", "stress test this", "ask me questions", wants to refine a plan before building, or before writing an implementation plan.
triggers:
  - grill me
  - 刨根问底
  - stress test
  - ask me questions
  - refine plan
---

# Grill Me

Interview me relentlessly about every aspect of this plan until we reach a shared understanding. Walk down each branch of the design tree, resolving dependencies between decisions one-by-one.

## Rules

1. **One question at a time** — ask, wait for my answer, then ask the next.
2. **For each question, provide your recommended answer** — don't just ask, suggest what you think is the right call. I'll correct you if you're wrong.
3. **Explore the codebase for answers** — if a question can be answered by searching existing code, do it instead of asking me.
4. **No fixed cap on questions** — keep going until every branch is resolved. Some plans take 3 questions, some take 50.
5. **When done, summarize** — produce a concise summary of every decision made. Save it to `.hermes/plans/` with a timestamp.

## Phases

### Phase 1: Scope
- What exactly are we building/changing?
- What's in scope? What's explicitly out of scope?
- Who is this for? What problem does it solve?

### Phase 2: Design decisions
- Walk through the architecture/implementation approach
- Surface trade-offs: "Option A means X, Option B means Y — which do you prefer?"
- Check for existing patterns in the codebase that should be followed

### Phase 3: Edge cases
- What happens when things go wrong?
- Error handling, boundary conditions, failure modes

### Phase 4: Acceptance criteria
- How will we know this is done?
- What tests matter most?
- What does "good" look like?

## Output

After grilling is complete, output a **Plan Summary** with:

```markdown
## Grill Summary
**Topic**: [what we discussed]
**Decisions**:
- [decision 1]
- [decision 2]
- ...

**Out of Scope**:
- [explicitly excluded items]

**Next**: [recommended action]
```

Save this to `.hermes/plans/grill-{topic}-{timestamp}.md`
