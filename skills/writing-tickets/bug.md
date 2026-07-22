# Bug

Defects in shipped behaviour — captures repro, observed result, and expected result.

## Template
```markdown
# Summary
Loading x results never loads when using filter y.

# Steps to Reproduce
1. Access portal [here](https://link.to.portal)
2. Click on thing
3. Filter for y

# Results
x results never loads, spinner keeps spinning, no feedback

# Expected Results
x results loads successfully, user is notified if there is an error

# Engineering Notes
- Logs: paste the key lines inline; link the [log-platform query](https://link.to/logs?query=...) as the source
- API implementation: `src/api/results.ts` ([permalink](https://github.com/org/repo/blob/<sha>/src/api/results.ts))
- UI filter trigger: `src/ui/filter.tsx` ([permalink](https://github.com/org/repo/blob/<sha>/src/ui/filter.tsx))
```

## Refinement Check
Before creating, verify:
- [ ] Steps to Reproduce are runnable by someone with only this ticket — environment URLs included, no local-only paths
- [ ] Relevant log lines are pasted inline, not only linked (queries go stale and may be access-gated)
- [ ] Code/file references pair a short path with a SHA-pinned permalink per [references/code-references.md](references/code-references.md)
