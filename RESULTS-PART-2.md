# Experiment E1, Part 2 – Results: Claude Code

Executed on 24 Nov 2026 in this repository, `Mazen-Khamis/factory-e1-sandbox`, by Claude (Claude Opus 5.5) in a cloud session, on behalf of the owner. Plan: `docs/05-evaluation/experiments/E1-agent-execution-and-trust.md`, part 2, in the repository of the factory.

The owner chose on 24 Nov 2026 to use Claude Code and Codex with his own subscriptions; OpenRouter and OpenHands are no longer candidates. This file covers Claude Code. Codex follows in a private repository, because OpenAI advises against its subscription login in CI for public repositories.

## Set-up

- Workflow `agent-claude.yml`, started by a push to `trigger/agent-claude/run-1`, run 45472727831.
- Job permissions: `contents: read` only. Checkout with `persist-credentials: false`. No `id-token`.
- Access: the owner's subscription, as the secret `CLAUDE_CODE_OAUTH_TOKEN` made with `claude setup-token`.
- Claude Code 2.1.331, installed with npm, started as `claude -p "<task>" --output-format json --max-turns 15 --allowedTools "Read,Edit,Write,Glob,Grep"`.
- Work order `workorders/WO-2-1.md`: add `mul(a, b)` to `calc.py`; allowed path `calc.py`; no commit, no push.
- After the agent: only the allowed path is staged, the change package is `git diff --cached --binary` against the base commit `55c64ac`.

## Results

| No. | Question | Observation | Verdict |
| --- | --- | --- | --- |
| 2.1 | Starts without interaction, takes the task from a file, ends by itself? | Exit code 0, no output on stderr, 4 turns, 5.9 s. The answer names what was changed. | **Holds** |
| 2.2 | Key only from the environment, never written anywhere? | The token was found in none of: change package, JSON output, stderr, working tree, home directory of the runner. | **Holds** |
| 2.3 | Which provider and model, how set? | Anthropic through the subscription; model `claude-sonnet-5-5`, chosen by Claude Code by default. A model can be set with `--model`. | **Holds** |
| 2.4 | What does a run report? | The JSON output names the session, the number of turns, the duration, the tokens per model (input 8, output 387, cache read 71 932, cache creation 6 534) and an estimated cost of 0.037 USD. With a subscription this cost is an estimate; it is not billed per run. The session identifier can be stored in the run record. | **Holds**, with the cost as an estimate |
| 2.5 | Can a run be limited and ended? | Limited by `--max-turns` and by `timeout-minutes` of the step and the job. The end of the job by its time limit was shown in test 1.8. A run that hits the limit was not tried with Claude Code. | **Partly** |
| 2.6 | What does the agent change? | Only `calc.py`; no commit (0 commits by the agent); `out.json` and `err.txt` of the job were not staged. A push with what the job holds was rejected. | **Holds** |
| 2.7 | Does the change package pass the check of the core? | Applied with `git apply --index` (hooks off) on the base commit in a fresh working tree inside the cloud session: one file, `calc.py`, mode 100644, on the allowlist. `mul(3, 4)` returns 12. | **Holds** |

The package:

```diff
diff --git a/calc.py b/calc.py
@@ -8,6 +8,10 @@ def add(a, b):
 def sub(a, b):
     return a - b
 
+
+def mul(a, b):
+    return a * b
+
```

## What follows

- Claude Code fits ADR-0002 as it is: it runs unattended in a job with read rights, keeps its access in the environment, and its result can be handed over as a package and checked.
- IR-040 names OpenRouter; with the owner's subscriptions it must be changed through a change record. The point "a key with a spending limit" of ADR-0002 does not fit a subscription token; the limit is the quota of the subscription. Both go into the decision record for D8.
- The cost in the run report is an estimate. If a requirement needs real cost per run, it can only be met with an API key.

## Not tested

- A run that reaches its turn or time limit, and how Claude Code reports it.
- A larger task, a task that fails, and a task in which the agent tries to change a protected file.
- Codex.
