"""Apply the prompt doctor's candidate edits to each case's champion prompt.

usage: python3 -I apply_candidates.py <loop_dir> [case_dir ...]

<loop_dir>/candidates.json   {"candidates":[{"id","hypothesis","edits":[{"old","new"}]}]}
<loop_dir>/<case>/sys_champ.txt   the current prompt for each case
Writes <loop_dir>/<case>/sys_<ID>.txt for every candidate and <case>/sys_ALL.txt
(all candidates combined), and prints for every edit which cases it applied to.
An edit whose "old" text matches no prompt, or more than once in a prompt, is
reported as UNMATCHED / AMBIGUOUS: fix the candidate before testing it.
"""
import json
import pathlib
import sys

loop = pathlib.Path(sys.argv[1])
cases = sys.argv[2:] or sorted(p.name for p in loop.iterdir() if (p / "sys_champ.txt").exists())
champ = {c: (loop / c / "sys_champ.txt").read_text() for c in cases}
cands = json.loads((loop / "candidates.json").read_text())["candidates"]

problems = 0


def apply(texts, edits, label):
    global problems
    out = dict(texts)
    for i, e in enumerate(edits):
        hit = []
        for c in cases:
            n = out[c].count(e["old"])
            if n == 1:
                out[c] = out[c].replace(e["old"], e["new"])
                hit.append(c)
            elif n > 1:
                print(f"   edit {i}: AMBIGUOUS in {c} ({n} matches)")
                problems += 1
        added = len(e["new"].split()) - len(e["old"].split())
        print(f"   edit {i}: applied to {hit or 'UNMATCHED'} ({added:+d} words)")
        if not hit:
            problems += 1
    return out


for cand in cands:
    print(f"== {cand['id']}: {cand['hypothesis']}")
    out = apply(champ, cand["edits"], cand["id"])
    for c in cases:
        (loop / c / f"sys_{cand['id']}.txt").write_text(out[c])

print("== ALL combined")
combined = dict(champ)
for cand in cands:
    combined = apply(combined, cand["edits"], cand["id"])
for c in cases:
    (loop / c / "sys_ALL.txt").write_text(combined[c])
print("problems:", problems)
