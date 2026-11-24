# Experiment E1, Part 2 – Results: Claude Code and Codex

Executed on 24 Nov 2026 by Claude (Claude Opus 5.5) in a cloud session, on behalf of the owner: Claude Code in the public repository `Mazen-Khamis/factory-e1-sandbox`, Codex in the private repository `Mazen-Khamis/factory-e1-private`. Plan: `docs/05-evaluation/experiments/E1-agent-execution-and-trust.md`, part 2, in the repository of the factory.

The owner chose on 24 Nov 2026 to use Claude Code and Codex with his own subscriptions; OpenRouter and OpenHands are no longer candidates. Codex ran in a private repository, because OpenAI advises against its subscription login in CI for public repositories.

## Claude Code

### Set-up

- Workflow `agent-claude.yml`, started by a push to `trigger/agent-claude/run-1`, run 45472727831.
- Job permissions: `contents: read` only. Checkout with `persist-credentials: false`. No `id-token`.
- Access: the owner's subscription, as the secret `CLAUDE_CODE_OAUTH_TOKEN` made with `claude setup-token`.
- Claude Code 2.1.331, installed with npm, started as `claude -p "<task>" --output-format json --max-turns 15 --allowedTools "Read,Edit,Write,Glob,Grep"`.
- Work order `workorders/WO-2-1.md`: add `mul(a, b)` to `calc.py`; allowed path `calc.py`; no commit, no push.
- After the agent: only the allowed path is staged, the change package is `git diff --cached --binary` against the base commit `55c64ac`.

### Results

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

## Codex

### Set-up

- Workflow `agent-codex.yml` in `factory-e1-private`, started by a push to `trigger/agent-codex/run-2`, run 45474795679. The first run (45474330494) stopped before Codex started, because the secret was not yet set.
- Job permissions: `contents: read` only. Checkout with `persist-credentials: false`. No `id-token`.
- Access: the owner's ChatGPT subscription. `auth.json` from `codex login` on the owner's machine, with `cli_auth_credentials_store = "file"`, is the secret `CODEX_AUTH_JSON`. The job writes it to a folder outside the working tree, sets `CODEX_HOME` to it, and removes it at the end.
- Codex CLI 0.172.0, installed with npm, started as `codex exec --json --sandbox workspace-write --skip-git-repo-check "<task>"`.
- Work order `workorders/WO-2-2.md`, the same task as for Claude Code.

### Results

| No. | Question | Observation | Verdict |
| --- | --- | --- | --- |
| 2.1 | Starts without interaction, takes the task from a file, ends by itself? | Exit code 0; one line on stderr; events `thread.started`, `turn.started`, `item.started`, `item.completed`, `turn.completed`. | **Holds** |
| 2.2 | Key only from the environment, never written anywhere? | The login is of kind `chatgpt`. None of its eight token strings was found in the change package or the working tree. `auth.json` was not changed by the run, so the owner's local login stays valid. | **Holds** |
| 2.3 | Which provider and model, how set? | OpenAI through the subscription. **The events name no model.** The model must therefore be set explicitly with `--model` and recorded from that setting. | **Holds with a condition** |
| 2.4 | What does a run report? | `thread.started` gives a thread identifier; `turn.completed` gives tokens (input 102 336, of which 94 464 cached, output 613). No cost. | **Partly**: no model, no cost |
| 2.5 | Can a run be limited and ended? | By `timeout-minutes` of the step and the job. Not tried to its limit. | **Partly** |
| 2.6 | What does the agent change? | Only `calc.py`; no commit. Codex also ran the acceptance test and its own checks inside its sandbox, and said so. A push with what the job holds was rejected. | **Holds** |
| 2.7 | Does the change package pass the check of the core? | Applied on the base commit `6e4defd` in a fresh working tree inside the cloud session: one file, `calc.py`, mode 100644, on the allowlist; `mul(3, 4)` returns 12. | **Holds** |

### Observed about the log

GitHub masks a multi-line secret line by line. In the public part of the log, the characters `{` and `}` were replaced by `***` wherever they appeared, because they are lines of `auth.json`. A token printed alone, without the rest of its line, would not be masked. This confirms the advice of OpenAI not to use this login in a public repository.

### Not tested for Codex

- A run that reaches its time limit.
- Whether the login keeps working over many runs. The refresh token in `auth.json` can be exchanged during use; in this run it was not. OpenAI describes writing an updated file back to the secret store for regular use.

## What follows

- Both agents fit ADR-0002 as it is: they run unattended in a job with read rights, keep their access in the environment, and their result can be handed over as a package and checked.
- Claude Code reports the model and an estimated cost per run; Codex reports neither. For Codex the model is set with `--model` and recorded from that setting (DR-021).
- Codex with a subscription needs a private repository. On GitHub Free a private repository has no rulesets and no branch protection, so the protection of ADR-0005 and ADR-0006 needs GitHub Pro there.
- IR-040 names OpenRouter; with the owner's subscriptions it must be changed through a change record. The point "a key with a spending limit" of ADR-0002 does not fit a subscription token; the limit is the quota of the subscription. Both go into the decision record for D8.
- The cost in the run report is an estimate. If a requirement needs real cost per run, it can only be met with an API key.

## Not tested for Claude Code

- A run that reaches its turn or time limit, and how Claude Code reports it.
- A larger task, a task that fails, and a task in which the agent tries to change a protected file.
