# Self-Training Loop

A Claude Code skill that trains any prompt, writer or agent the way AI is trained: test with fresh no-context agents, score blind, have the judges write the ideal answer, let a prompt doctor propose three rival fixes, keep only what wins, and finish with a graph page of the whole climb.

## Install

```bash
git clone https://github.com/inventabotnow/self-training-loop-skill ~/.claude/skills/self-training-loop
```

Then in Claude Code say "self-training loop" (or ask to improve a prompt). It opens with: **What do you want to improve?**

## What is inside

- `SKILL.md` — the full method and the lessons learned.
- `report-template.html` — the end-of-run graph page (edit only the `REPORT` data block).
- `apply_candidates.py` — applies the doctor's find-and-replace fixes and flags mismatches.
