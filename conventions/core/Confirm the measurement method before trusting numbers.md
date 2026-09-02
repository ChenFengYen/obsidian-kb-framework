---
type: convention
rule_id: KB-VERIFY-001
applies_to: [all-agents]
triggers:
  - verification
keywords:
  - before-after-compare
  - scanner-script
  - self-test
enforcement: review
severity: warning
status: active
---
# Confirm the measurement method before trusting numbers

## In one line

> Before accepting a number as proof that your change is sound, check that the measurement itself is sound. **A broken measuring tool usually reports "clean" rather than failing.** The hardest case to catch is the tool that is wrong by the same amount every time - it looks the most trustworthy.

## Three ways a check passes while the work is broken

### 1. The tool silently reports zero

When a verification script finds nothing, the natural reading is "no problem". That is the danger: failure and success produce the same output.

Two measured examples, both from ordinary version-control tooling:

| What was run | What it reported | What was actually wrong |
|---|---|---|
| An object listing whose format string omitted the field carrying the remainder of each line | zero contaminated objects | Each "hash + path" line was parsed as a single object name, so every lookup missed |
| A changed-file listing scanned for a filename suffix | zero changed files | Non-ASCII paths came back quoted and escaped, so the suffix test never matched |

**Defence: any result that says 0, or 100%, or "all passed", must first be tested against a case known to match.** If the tool cannot find the known case, the tool is broken.

The mirror image happens too. A scanner searching for a range of private-use characters, written so that the range degraded into a character class containing a literal hyphen, matched every hyphen in the text and reported 41 defects in a clean file. A false positive is equally capable of causing a wrong decision; it merely fails loudly instead of quietly.

**General defence: give the scanner its own self-test.** Assert both directions - that it finds a known bad case, and that it does not flag known-good content - and trust the result only when both hold.

```python
assert scan(known_bad),        "misses a known defect -> the tool is broken"
assert not scan(known_good),   "flags clean content -> the pattern is too wide"
```

### 2. The total is moving, so only a difference attributes anything

Whole-repository statistics are unreliable as before-and-after evidence whenever anything else can write to the repository between the two runs - a background auto-commit, a second machine, a collaborator.

A measured example: after one cleanup pass a broken-link count rose from 22 to 25. Attributing that to the cleanup would have sent someone to fix a problem that did not exist. Extracting the baseline commit's tree, computing the unresolved-link set on both, and taking the set difference showed that all 24 new ones arrived with someone else's import that day, and the cleanup introduced zero.

**Defence: to claim "I did not break anything", produce a set difference with the offending items named.** Totals are for trends, not for attribution.

### 3. The tool is wrong by a constant

The first two classes announce themselves - a suspicious zero, a jumping number. The dangerous one is the tool that is off by the same amount every time. It is self-consistent, the trend is right, the differences are right; only the absolute value is wrong, which is exactly why it looks credible.

A measured example: a per-commit file count produced a clean descending curve, and every step matched the number of deletions in that commit. Every value was nevertheless one too high. It was found by counting a second way - listing from version control and from disk and comparing the sets - which agreed with each other and disagreed with the first tool.

**Defence: compute any load-bearing absolute value a second, independent way.** Running the same tool twice proves it is stable, not that it is correct; a systematic offset hides behind exactly that stability.

Corollary: when reporting a number, check whether independent arithmetic explains it - start, minus removals, equals end. **If it does not reconcile, investigate the measurement before revising the conclusion.**

**Why repeating the measurement does not help here.** Averaging $K$ independent evaluations shrinks variance as $\mathcal{O}(1/K)$ but leaves bias untouched; published work on repeated LLM evaluation finds most of the available gain is consumed between one and four repetitions. Repetition addresses random scatter, not an error that recurs identically.

**This extends to asking an agent again.** Pressing "are you sure?" in the same conversation is worse than an independent repeat: the follow-up is conditioned on the previous answer, which maximises the correlation between the two samples. If the first answer came from misreading the source, the second will repeat it with more confidence. Change the instrument instead - require quotes from the source, check against material that does not share the current context, or change the presentation and ask again.

## This rule is a hub

The claim above is the shared criterion. Related rules each handle one concrete shape of the same structure: **"the check passed" and "the work is correct" come apart somewhere, and nothing signals it.** Known shapes include a tool that omits by default and therefore reports clean; a configuration string standing in for the state it describes; a monitoring baseline that never expires; and automated checks that are structurally blind to one class of defect.

When a new failure of this type appears, return to the judgement question below. **If you can name the failure signal, you have a check; if you cannot, this family has gained another instance.** Whether that becomes a new rule or an example under an existing one depends on where the decoupling happens.

## Judgement question

**If my change is in fact broken, how exactly would this check tell me?**

If you cannot name a concrete failure signal, the check verifies that a script ran, not that the result is right.

## Related

- `Do not invent facts or thresholds` - numbers need a source; this rule adds that the *way* a number was produced needs verifying too.
- `Approval before destructive or published changes` - verification numbers are the evidence approval rests on, so the evidence itself must be sound.
- `Ignore rules must survive directory renames` - the same family: a rule bound to a string, silently void once the environment changes.
- `Counterbalance presentation order in paired comparison` - the same principle applied to judgements with no number to check: this rule changes the instrument, that one changes the position.
