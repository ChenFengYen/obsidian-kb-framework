---
type: convention
rule_id: KB-CHANGE-002
applies_to: [all-agents]
triggers:
  - destructive-op
keywords:
  - anchored-replace
  - prefix-collision
  - shell-quoting
enforcement: review
severity: error
status: active
---
# Enumerate every match before a batch replacement

## In one line

> A batch string replacement must be anchored to complete, known targets, and every match must be listed and confirmed before it runs. A generic replacement on a prefix or substring silently destroys unrelated text that happens to share it - with no error and no trace.

## The prefix is not the target; the folder names are

The vault this framework was extracted from once dropped an `OV-` prefix from nine domain folder names. Running `s/OV-//g` would also have destroyed `OV-DETR` - Open-Vocabulary DETR, a model name with nothing to do with the folder prefix, 4 occurrences, all in one paper note. The note would then name "DETR" where a different model was meant, and a semantic error like that has no syntactic symptom.

What was actually done: anchor to the **nine known, complete folder names**, protect the model name with a sentinel first, and verify afterwards that the 4 occurrences are intact.

The general form: the target of a replacement is **a known set of strings you can list in full**, not a pattern. A pattern matches things you did not think of, and what you did not think of you will not look at.

## Measure the reach before acting

The same operation, as enumerated before it ran:

| Affected | Count |
|---|---|
| notes | 62 files, 739 occurrences |
| scripts | 6 (at most 59 occurrences in one file) |
| documentation | 5 files |
| permission settings and skills | a permission glob, 3 skills |

**Wikilinks were not affected at all; path strings were.** That distribution was not guessed - it is what enumeration showed, and it decided both which files to check and which never needed touching. The editor's own state directory was excluded: it is ignored by version control, rebuilt automatically, and rewriting it while the application runs only invites trouble.

## Do not pass long content through the shell

The second silent failure sits on the delivery path. Passing a long string containing backticks to `python -c` inside a shell makes the shell **execute the backticks as command substitution**, and the result of that is what lands in the file. The script itself was entirely correct; what broke was the stretch before the content arrived.

Rule: **write long content to a file first, then have the program read that file.** Nothing passes through the shell, so there is nothing to quote, escape, or substitute. Likewise, keep non-ASCII replacement literals off the command line, where the console's encoding gets a say in them.

## Judgement question

**If I replaced the wrong target, how would this run tell me?**

Usually it would not: the exit code is 0, the files still parse, and the damage is to meaning. So the match list has to be produced and read **before** the run; checking afterwards is too late.

## Related

- `Windows UTF-8 file safety` (windows-zh-tw pack) - a clear boundary: that rule governs whether the bytes written out are right, this one whether the replaced targets are right. Both fire on the same batch rewrite and guard different failures.
- `Ignore rules must survive directory renames` - the same family: a rule bound to a string goes silently dead when the environment changes.
- `Approval before destructive or published changes` - a batch rewrite needs approval, and the match list is the evidence that approval rests on.
- `Confirm the measurement method before trusting numbers` - the check after a replacement is itself a measurement; "4 occurrences verified intact" can be false too.
