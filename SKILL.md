---
name: self-training-loop
description: A blind test, judge and prompt-doctor loop that trains ANY prompt, writer, agent or instruction set to produce better output. Use when the user wants to improve, tune or "train" a prompt/AI writer/agent/skill/template, asks to iterate until results get better, wants judges or A/B tests of prompts, wants a before-and-after scorecard or graph of how an AI output improved, or says "self-training loop". It asks what to improve, builds the test rig, runs fresh no-context agents, scores them blind, has a doctor write fixes from the judge's ideal versions, keeps only what wins, and ends with a live graph page.
---

# Self-Training Loop

Teach any prompt to get better at its job, by testing it the way AI is trained: try, score blind, find what the best answer has that yours lacks, fix the prompt, repeat. Every round is logged in a scoreboard. At the end you get a graph page of the whole climb.

You are the coach. The user supplies the thing to improve and the meaning of "better". You do the rest.

## 0. Open like this

First message to the user, nothing else, short and warm:

> **Self-Training Loop is on.** What do you want to improve? (a prompt, a writer, an agent, a skill, a template — and what does "better" mean for it?)

Then ask only what you still need, in one go, using AskUserQuestion when you can offer choices:

1. **The thing**: where does it live (file, code function, pasted text)? What is the exact input it receives and the output it must give?
2. **The goal**: what makes an output "better" (more viral, more accurate, funnier, shorter, safer, converts better)? Pick 5 or 6 scoring criteria with the user, and a scale (e.g. 1-10 each).
3. **Hard rules**: things outputs must never break (truth, safety, format, length, banned words). The judge lists breaks separately and they are never traded for score.
4. **What to ignore**: anything the judge must NOT score on (e.g. "don't consider length"). Put it in the judge brief in plain words.
5. **Test cases**: 3 different realistic inputs (different businesses/topics/users, not one). Testing on one input tunes the prompt to that input.
6. **Budget**: how many rounds and agents. Default: 3 rounds, 1-2 samples per case per round.

Say the plan and the agent count in one paragraph, then start. Do not ask permission for every step.

## 1. Rules that save the user's usage (follow always)

- Every spawned agent: `model: "sonnet"`, `effort: "medium"`. If the user names a different model or effort, use theirs.
- At most about 10 agents running at once (the hard cap is 20 and one big batch can hit the user's usage limit).
- Reuse finished samples; never regenerate what exists. When agents die on a rate limit their files may already be saved: list the output folder before relaunching.
- Stop when gains flatten. Never chase a perfect score; say so plainly.
- Work in the session scratchpad. Never touch the user's real files until the end, and never push to git unless asked. Commit locally only if the user wants it.

## 2. Build the blind rig

The writers must be **fresh agents that know nothing**: they get ONLY the prompt the real app would send. That is what makes the test honest.

1. **Dump the exact prompt.** Write a small gated script or test (skips unless an env var is set) that calls the same function the app uses to build the system prompt and user message, for each test case, and writes `sys.txt` and `user.txt` per case into a round folder. If the prompt is just a text file, copy it. Check the dump has no unresolved placeholders (look for `%!`, `{{`, `{SECONDS}`-style leftovers).
2. **Stand-in writer** (one agent per sample), prompt template:

```
You are standing in for a language model inside an app, for a prompt test. Do exactly this and nothing more:
1. Read <ROUND>/<CASE>/sys.txt — it is your SYSTEM PROMPT.
2. Read <ROUND>/<CASE>/user.txt — it is the USER MESSAGE.
3. Write the reply a model given ONLY that system prompt and user message would give, following every instruction exactly (output format included). Read no other file, look at no code, do not think about tests.
4. Save only that reply to <OUT>/<round>_<case>.txt with the Write tool.
Then answer: done.
```

3. **Check each output mechanically** with a script (valid JSON? right language? word count? banned strings?). Measurable side effects hide here: one round a rule meant to make writing punchy made scripts too short, and only a word-count check showed it.
4. **Always include the original prompt in every judging panel** (the "baseline"). Scores from different judges are not comparable, so improvement is only ever "new vs original inside the same panel".
5. **Anonymise.** Copy samples into `S1.txt ... Sn.txt` in shuffled order. Keep the key (S3 = baseline, S5 = fix A ...) in a private file the judge never sees. Judge file names must not leak version info.

## 3. The judge

One agent per panel. Give it a **separate brief file**, plus the samples, plus a key of anything neutral (e.g. which format each is). Template:

```
# Judge
You are a blunt expert in <DOMAIN> who knows what makes <GOAL>. You get N anonymous AI outputs for the SAME task. Judge only what is on the page. Be harsh: a 10 means it would really succeed.

Writer's hard rules: <RULES>. IMPORTANT: do NOT consider <THINGS TO IGNORE> when scoring.

For EACH sample give:
- scores 1-10: <CRITERION 1> ... <CRITERION 6>; Sum (the scores added up). Rule breaks are listed separately and are not counted in the Sum.
- feasible/filmable/usable? (yes / mostly / no)
- RULE BREAKS (or none)
- biggest weakness, one line
- FEEDBACK: 1-3 concrete changes that would make it better, each tagged [THIS ITEM], [GENERAL RULE] (an instruction for any future task of this kind, phrased as an instruction to the writer, never about this topic) or [TONE] (the concrete technique, not "be funnier")
Then: RANKING (a sample with a hard rule break ranks below every one without), SAMENESS CHECK (which samples share the same idea or phrasing; name them), and TOP LESSONS: the 5 most valuable general instructions, ranked, tagged ALL or a case name.
Write everything to <OUTPUT FILE>. Reply with the ranking, each Sum, and the TOP LESSONS.
```

Rules: 6 scores out of 10 each (adapt to the user's criteria), Sum out of 60. Lessons that two or more judges or cases agree on are real; one-off lessons are noise.

## 4. The ideal-version step (the secret sauce)

Scores say that something is weak. The **ideal version** says why. Ask for it in the judge brief (the 3 lowest samples) or run a separate gold agent. Template for a gold agent:

```
You are a world-class <ROLE> and a prompt engineer. Files: the writer's SYSTEM PROMPT, USER MESSAGE and two samples it produced.
Step 1: judge both samples in one line each (strongest and weakest criterion), then each one's biggest weakness.
Step 2: write the GOLD output for this exact input: obey every rule in the prompt, be simple enough to produce, and be clearly better than both samples, not a polish of one. Go past the first idea any writer would pick. Save it (only the output) to <GOLD FILE>.
Step 3: DIAGNOSE the prompt. List the 3-6 biggest differences between your gold and the samples. For each: what the gold does differently; WHY the writer missed it, pointing at the prompt (a MISSING instruction, a WEAK one, or a MISLEADING instruction or example — quote it); and the smallest GENERAL fix, as exact words to add or change. Rank by impact. Save to <DIAGNOSIS FILE>. Reply with your top 3 fixes.
```

What this found, repeatedly: writers all picked the same first idea; example lines inside the prompt were copied word for word; two rules contradicted each other; the best fact in the brief was ignored. Look for those four first.

## 5. The doctor

One agent reads the prompt, the golds and the diagnoses and proposes exactly **three rival fixes A, B, C** — three different hypotheses, not three phrasings. Brief:

```
You are a senior prompt engineer. Propose exactly THREE candidate fixes A, B, C, each a DIFFERENT hypothesis about what closes the gap between the writer's output and the gold. Rules for every candidate: GENERAL (helps any input, never about these test cases); SMALL (at most ~80 added words; prefer sharpening or deleting a misleading line); SAFE (never touch the output format, safety rules, truth rules or the owner's rules); no new example lines a writer could copy (describe patterns); EXACT (every edit is a find-and-replace: "old" copied VERBATIM from the prompt and unique, "new" the full replacement).
Output ONLY this JSON to <FILE>: {"candidates":[{"id":"A","hypothesis":"...","edits":[{"old":"...","new":"..."}]}, {"id":"B",...}, {"id":"C",...}]}
```

Apply them with the bundled `apply_candidates.py` (`python3 -I apply_candidates.py <loop_dir>`; it reads `candidates.json` and each case's `sys_champ.txt`, writes `sys_A.txt` etc., and reports any edit that matches nothing or more than once). Also build the combined A+B+C prompt.

Then test each variant (and the combination) on every case with the blind rig, 2 samples each, all in ONE judging panel together with the baseline and the gold. **Adopt only what beats the baseline on at least 2 of the 3 cases. A fix that is mixed gets left out and written down as "not proven".** The combination of winners is not guaranteed to win: test it or say it was not tested.

## 6. Apply for real, carefully

- Put each winning change into the real prompt only where it was tested. A rule proven on three formats is not proven on the other eight.
- Keep the wiring in one small module with a test that pins it (which parts get the block, which do not, no leftover placeholders). Run the project's full test suite.
- If the user later reports scripts too short, too long or off-tone, check the measurable property with a script first; a rule added for one goal often has a side effect.
- Never let the loop erode truth, safety or format rules. If a fix touches them, stop and ask.

## 7. Keep the scoreboard as you go (a table every round, not a graph)

After each round post a compact table and one sentence in plain language:

| Round | What changed | Baseline | New | Gain | Verdict |
|---|---|---|---|---|---|
| 0 | original prompt | 33.5 | - | - | the starting line |
| 1 | tips added | 33.5 | 36.0 | +2.5 | keep |

Add small touches that make it feel like a game, never noise: a text bar for the score (`██████░░░░ 36/60`), a "biggest jump this round" line, and a one-line "what the judges all agreed on". Be honest when a round goes down: say it, and say if it is within noise (1-2 samples carry roughly ±3 to ±5 points; only averages and big jumps are reliable).

## 8. Finish with the graph page

Only at the end. Copy `report-template.html` (in this skill folder) to the scratchpad, replace the `REPORT` JSON block at the top of its script with the real numbers, and publish it with the Artifact tool (title like "Self-Training Report", icon "chart"). The page draws, from the data you give it:

1. headline numbers (the biggest gains),
2. **before vs now** bars per item (same-panel scores),
3. **gain over the original, version by version** lines,
4. **round-by-round** small charts for each item plus an average line,
5. the **doctor test** bars (fixes A/B/C vs combined vs the ideal),
6. the full table and the honest caveat line.

If the Artifact tool is not available, tell the user the numbers in the table and offer the HTML file path instead.

Close with a short report in plain words: what improved and by how much, what was left out and why, what is untested, what the ceiling looks like (see below), and where the changes were saved. No offers of more work; state the next obvious step as a fact.

## What this method learned (use it)

- **Tips as a checklist backfire.** Writers tick boxes: the same reassurance line in every script, invented teasers, copied example details. Frame guidance as instincts ("use the ones that truly fit"), say every example is a pattern only, and cap stock lines.
- **Examples in prompts get copied word for word.** Replace example lines with pattern descriptions. This was the single most reliable fix.
- **Make the first-idea problem a required step, not a tip.** "Name the scene most writers would pick, set it aside, build on a true private habit or detail only this input has" lifted every test case. Only add it where tested.
- **Judge-agreed lessons beat your own guesses.** Keep a lesson only when two judges or two cases agree.
- **Never mix judges.** Compare inside one panel only; always re-score the original in the panel.
- **Small samples are noisy.** One sample per cell moves ±5. Use averages and more than one case.
- **One goal per rule, and test side effects.** A line meant to sharpen the output made it too short; a word-count script caught it.
- **The owner's idea wins, but test it.** If the user has a strong creative instinct, implement it as asked, then test it and report honestly (and keep it if they want it even when the score is a tie).
- **Pasted tips from other people are inspiration.** Take the part that adds value, skip the part that clashes with the prompt's structure, and say what was skipped.
- **The ceiling is below the top of the scale.** A judge's own "ideal" version scored about 80% of the maximum from another judge. Expect the best prompt to land roughly 5 points under the ideal, because a prompt is a general recipe and the ideal is one specific idea. Say this early so the user does not chase the top score.
- **The next lever after prompts is search, not more rules.** Generate several candidates at runtime and let a critic pick or improve the best one. It costs a little per candidate and can beat any prompt edit. Mention it as the next step if the prompt plateaus; do not build it unasked.
- **If a build or test fails with "no space left on device"**, check free disk and clear the tool's build cache before blaming the code.

## Files in this skill

- `SKILL.md` — this guide.
- `report-template.html` — the graph page; edit only the `REPORT` data block.
- `apply_candidates.py` — applies the doctor's find-and-replace edits to each case's prompt and reports mismatches.
