---
type: convention
rule_id: KB-VERIFY-002
applies_to: [all-agents]
triggers:
  - option-compare
keywords:
  - pick-one
  - ranking
  - positional-bias
  - subjective-judgement
enforcement: review
severity: warning
status: active
---
# Counterbalance presentation order in paired comparison

## In one line

> When an agent is asked to choose between two options, **the order they are presented in changes the answer.** A comparison must place each option in each position once and combine the results; at minimum, swap the order and ask again. Instructing the model to ignore order does not work.

## The evidence

Published measurements of LLM-as-judge pairwise evaluation report **conflict rate** - the same pair queried twice with positions swapped, and the fraction of pairs where the two verdicts disagree. Representative figures from an 80-question benchmark with 2023-2024 models:

| Judge | Pair | Win rate in position 1 | Win rate in position 2 | Conflict rate |
|---|---|---|---|---|
| Stronger judge | close pair | 51.3% | 23.8% | 46.3% |
| Stronger judge | distant pair | 92.5% | 92.5% | 5.0% |
| Weaker judge | close pair | 2.5% | 82.5% | 82.5% |
| Weaker judge | distant pair | 37.5% | 90.0% | 52.5% |

The third row is the striking one: same answers, same judge, only the order swapped, and the win rate moves from 2.5% to 82.5%.

Later work on ranking $N$ candidates treats the countermeasure as a required engineering step rather than an optional check: walk a random Hamiltonian cycle so each candidate appears exactly once in each slot of the prompt, letting the model's systematic positional preference cancel around the cycle.

## Three findings that shape the rule

### Instructions do not help; structure does

The evaluation template used in those measurements already contained an instruction not to let ordering affect the judgement. The conflict rates above were measured **with that sentence in the prompt**. The rule therefore requires positional balance in the procedure, not wording in the prompt.

### The direction of the bias varies, so cancel it rather than correct for it

One judge favoured the first position, another the second, and stronger models were less affected. Since the direction changes with model and version, you cannot assume a fixed direction and compensate against it. Placing each option in each position once is the only robust form.

The same reasoning bounds what may be cited: **the phenomenon and the countermeasure transfer; the magnitudes do not.** Do not quote these rates as current behaviour.

### The closer the options, the more this matters

Conflict rate correlates negatively with the quality gap between the two candidates: near-tied pairs are strongly order-dependent, clearly separated pairs are stable.

This inverts the intuition that the check is usually unnecessary. **Nobody asks an agent to choose between two options with an obvious winner - the ones people actually bring are the close ones**, which is precisely the regime where the bias is strongest.

## How to apply

- **When asking for a choice**: swap the order and ask again, or require the agent to state in the same answer whether reversing the order would change the verdict. **Two different verdicts mean the comparison has no result** - go back for more evidence rather than trusting either run.
- **When the agent itself proposes several options**: the same applies, and it is less visible, because the agent chose the ordering. Its preference for the option it wrote first carries into the argument that follows.
- **Cost**: one extra query. Reported agreement with human judgement improved by roughly 10-14 percentage points when evidence calibration and positional balancing were applied together.
- **Not applicable**: comparisons with a checkable ground truth - which number is larger, which script errors, whether a file exists. Positional bias affects judgement calls, not facts you can verify directly.

## Judgement question

**If this conclusion is an artefact of ordering, where would I see that?**

If there is no answer, the comparison was run in one arrangement only and its stability is untested.

## Related

- `Confirm the measurement method before trusting numbers` - the same family: that rule recomputes a load-bearing number a second way, this one re-asks a comparison from a second position. Shared premise: **one instrument used twice proves stability, not correctness.**
- `Prefer simple justified methods` - positional balancing costs one query, which beats any countermeasure requiring a redesign.
- `Approval before destructive or published changes` - choosing between plans usually precedes approval; an unstable verdict should not enter it.
