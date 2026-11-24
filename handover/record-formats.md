# Specification: Record Formats

Status: Draft 3, 24 Nov 2026. Defines the formats that [03-data.md](../../02-requirements/03-data.md), "Record Formats Required for Stage A", asks for. Adds no scope. Follows [ADR-0005](../adr/ADR-0005-approvals-and-merge.md) and [ADR-0006](../adr/ADR-0006-records-branch.md).

## 1. General rules

1. **Files.** Every artifact and every record lives in the project repository (DR-001) and is written in YAML, so that a person can read it without the factory (DR-004). Each is one file, except evidence: one logical record made of `evidence.yaml` and three files kept unchanged (section 6).
2. **Schemas.** Each kind has a JSON Schema under `schemas/` in the repository of the factory, named by the value of the field `schema`. The factory refuses a file that does not conform and names the file and the reason (FR-007). The schemas hold no project content (DR-003).
3. **No status.** No file holds a status of a requirement, a task or a run. Status is derived from records (DR-020, DR-043).
4. **Not reported.** A value that a source does not report is written as the string `not reported`. It is never guessed (DR-021).
5. **Time.** Every time is UTC in the form `2026-11-24T20:15:03Z`.
6. **Encoding.** UTF-8, line ending LF, no byte order mark.

## 2. Where files live

| Branch | Path | Kind | Written by |
| --- | --- | --- | --- |
| default | `.factory/frame.yaml` | frame | human |
| default | `.factory/allowed_signers` | list of permitted signers | human |
| default | `requirements/REQ-NNNN.yaml` | requirement | human |
| default | `tasks/TASK-NNNN.yaml` | task | human |
| default | paths named by a task | acceptance tests | human |
| `factory-records` | `approvals/states/APR-….yaml` | approval of states before a start | human |
| `factory-records` | `approvals/changes/<commit>/APR-….yaml` | approval of a change | human |
| `factory-records` | `workorders/WO-….yaml` | work order | factory |
| `factory-records` | `runs/RUN-….yaml` | run record | factory |
| `factory-records` | `evidence/EV-…/` | evidence (four files, section 7) | factory |
| `factory-records` | `blockers/BLK-….yaml` | blocker | factory |
| `factory-records` | `decisions/DEC-….yaml` | decision that closes a blocker | human |

Artifacts on the default branch change only through an approved pull request (ADR-0005). Records on `factory-records` are added once and never changed (ADR-0006): **one record per commit**, and that commit is signed with the key whose role matches the field `by` of the record. The path of a change approval contains the full commit identifier, so that `approval-gate` finds it.

## 3. Identifiers

| Kind | Form | Assigned by |
| --- | --- | --- |
| Requirement, task | `REQ-0001`, `TASK-0001`, numbered in sequence, never reused | human |
| Records | `<KIND>-<time>-<6 hex>`, for example `RUN-20261124T201503Z-3f9a0c` | factory, from the time of creation and 3 random bytes |

`<KIND>` is one of `APR`, `WO`, `RUN`, `EV`, `BLK`, `DEC`. Before it writes a record, the core checks that the identifier does not exist yet on the records branch; if it does, it makes a new one. It never overwrites a record. The run identifier is assigned before the start and written into the work order (IR-008, DR-024). Links between files use these identifiers only (DR-006).

## 4. State identifier

A state is identified by `sha256:` followed by the SHA-256, in lower-case hex, of a canonical list (DR-005, D6):

- one line per file of the set: `<Git file mode>` TAB `<path>` TAB `<Git blob identifier of the file>` LF, for example `100644\ttests/acceptance/test_truss_forces.py\t3b18e5…`;
- lines sorted by path, byte by byte;
- the hash is taken over the UTF-8 bytes of the whole list.

| State | Set of files |
| --- | --- |
| frame state | `.factory/frame.yaml` and `.factory/allowed_signers` |
| requirement state | the file of the requirement |
| task state | the file of the task |
| test state | every file that defines the acceptance tests: the test files the task names in `acceptance_tests` and the helpers, fixtures and `conftest.py` files it names in `test_support` |

The state of an implementation is the commit identifier of the task branch (40 hex). Records are never part of a set, so writing a record changes no state.

## 5. Artifacts

**Frame** (`.factory/frame.yaml`)

```yaml
schema: factory/frame/1
project: trusscalc
owner: owner@role-human             # principal in .factory/allowed_signers
approvers: [owner@role-human]       # SR-005; stage A: the owner only
confidentiality: open               # open | restricted | local only (SR-040)
agent: claude-code                  # adapter used for this project (ADR-0007)
```

In stage A the factory works on `open` and `restricted` projects and refuses `local only`, because the agent runs in the cloud. A `restricted` project is a private repository and needs the rules of ADR-0005 and ADR-0006, which on GitHub need a paid plan (ADR-0007).

**Requirement** (`requirements/REQ-NNNN.yaml`)

```yaml
schema: factory/requirement/1
id: REQ-0001
statement: The calculator returns the axial force of every member of a statically determinate plane truss.
acceptance_criteria:
  - For the three-member example truss, the forces match the reference values within 1e-9.
```

**Task** (`tasks/TASK-NNNN.yaml`)

```yaml
schema: factory/task/1
id: TASK-0001
requirement: REQ-0001
acceptance_tests: [tests/acceptance/test_truss_forces.py]
test_support: [tests/acceptance/conftest.py]   # every other file the tests use; may be empty
allowed_paths: [src/trusscalc/]      # allowlist of the change package (ADR-0002)
instruction: Implement the axial-force calculation so that the acceptance tests pass.
limits: {time_minutes: 20, turns: 30, runs: 3}   # SR-008
model: claude-sonnet-5-5             # always set explicitly (ADR-0007)
```

## 6. Records

Every record starts with these fields, `evidence.yaml` included; all four are required:

```yaml
schema: factory/<kind>/1
id: <identifier>
created: 2026-11-24T20:15:03Z
by: owner@role-human                 # or factory; must match the role of the signing key
```

**Approval of states** (`approvals/states/APR-….yaml`), before a start (FR-020, FR-031, SR-023). It covers the frame, the requirement, the task and the tests; a start needs all four in their current states.

```yaml
covers:
  - {kind: frame, ref: trusscalc, state: "sha256:…"}
  - {kind: requirement, ref: REQ-0001, state: "sha256:…"}
  - {kind: task, ref: TASK-0001, state: "sha256:…"}
  - {kind: tests, ref: TASK-0001, state: "sha256:…"}
note: optional text
```

**Approval of a change** (`approvals/changes/<commit>/APR-….yaml`), before a merge (FR-022)

```yaml
covers:
  - {kind: change, ref: TASK-0001, commit: "<40 hex>", evidence: EV-…}
note: optional text
```

An approval is valid only for exactly the states or the commit it names (FR-031).

**Rule for a merge.** A change approval counts only if all of the following hold:

- the evidence it names exists on the records branch, written by the factory in a commit signed with the recording key;
- its `result` is `passed`, its `implementation_commit` is exactly the commit of the approval, and its `test_state` is the test state approved before the start;
- its `result.json` is verified again by `approval-gate` itself against the attestation of GitHub (ADR-0004), online, with the expected signer workflow and repository, and the verified file states the same commit, test state and result.

The last point does not rely on the records of the factory, so a stolen recording key cannot make a change pass. The stored bundle and trusted root serve later checks without the platform (DR-025). How `approval-gate` does this is defined in the specification of GitHub and CI.

**Work order** (`workorders/WO-….yaml`), written before the start (DR-024). The instruction is copied in, so that a work order can be read on its own.

```yaml
run: RUN-…
task: TASK-0001
base_commit: "<40 hex>"
starts_from:
  approval: APR-…
  states: {frame: "sha256:…", requirement: "sha256:…", task: "sha256:…", tests: "sha256:…"}
instruction: <text of the task>
allowed_paths: [src/trusscalc/]
limits: {time_minutes: 20, turns: 30}
adapter: claude-code
model_requested: claude-sonnet-5-5
```

**Run record** (`runs/RUN-….yaml`), written after the end is confirmed (DR-026, DR-021, IR-005)

```yaml
work_order: WO-…
started: …                         # "not started" when the reason is start_failed
ended: …
outcome: completed                   # completed | failed | interrupted
reason: {code: none, text: ""}       # see the codes below
provenance:
  adapter: {name: claude-code, version: "1"}
  agent: {name: Claude Code, version: "2.1.331"}
  provider: anthropic
  model_requested: claude-sonnet-5-5
  model_reported: claude-sonnet-5-5  # or "not reported"
  parameters: {max_turns: 30, allowed_tools: [Read, Edit, Write, Glob, Grep]}
  usage:                             # as the agent reports it, or "not reported"
    tokens: {input: 8, output: 387, cache_read: 71932, cache_creation: 6534}
    cost_usd: 0.0372
    cost_is_estimate: true
  session: e6688ffc-…                # identifier the agent reports, or "not reported"
  platform_run: {id: "45472727831", url: "https://github.com/…/actions/runs/45472727831"}
package: {sha256: "…", files: [src/trusscalc/forces.py]}   # or "none"
implementation_commit: "<40 hex>"  # commit the core wrote to the task branch from the package, or "none"
```

Reason codes: `none`, `start_failed`, `time_limit`, `turn_limit`, `agent_error`, `package_rejected`, `cancelled`. Outcome `completed` has reason `none`; `failed` and `interrupted` never do (IR-005).

A run record exists only when the end of the run is confirmed. The life of a run in records:

| Situation | Records |
| --- | --- |
| Work order written, run may be active | work order, no run record. The run counts as open; no second run starts for the task (FR-067). |
| Run ended, `completed` | run record |
| Run ended, `failed` or `interrupted` | run record and a blocker |
| Start refused by the platform | run record with outcome `failed`, reason `start_failed`, and a blocker |
| Status of the run cannot be established | a blocker with reason `status_unknown` that names the run and the work order; **no run record**. The run stays open until its end is confirmed. |

**Evidence** (`evidence/EV-…/`), four files (DR-022, DR-025, ADR-0004)

| File | Content |
| --- | --- |
| `evidence.yaml` | the fields below |
| `result.json` | the result file of the verification run, unchanged |
| `bundle.jsonl` | the bundle of the attestation |
| `trusted_root.jsonl` | the trusted root, taken by the core from GitHub |

```yaml
task: TASK-0001
work_order: WO-…
agent_run: RUN-…
implementation_commit: "<40 hex>"
base_commit: "<40 hex>"
test_state: "sha256:…"
verification:
  run: {id: "…", url: "…"}
  definition: .github/workflows/verify-trusted.yml@<commit of the default branch>
  environment: {runner: ubuntu-24.04, python: "3.14.0"}
  seeds: none                        # or the seeds used
result: passed                       # passed | failed | not executable
attestation: {verified: true, signer_workflow: "…", repository_id: "…"}
```

**Blocker** (`blockers/BLK-….yaml`) (DR-027)

```yaml
reason: {code: time_limit, text: The run ended at its time limit of 20 minutes.}   # codes: the reason codes of a run, status_unknown, verification_failed, verification_not_executable, rule_missing. Invalid records are reported, never recorded as a blocker on the same branch (ADR-0006)
affects: {task: TASK-0001, run: RUN-…}   # run may be "none"
event: {kind: run_ended, ref: RUN-…}   # kinds: run_ended, start_refused, status_unknown, verification_failed, verification_not_executable, rule_missing
```

**Decision that closes a blocker** (`decisions/DEC-….yaml`) (FR-066, DR-027)

```yaml
blocker: BLK-…
decision: retry                      # retry | abandon
reason: Limit raised in TASK-0001; start once more.
```

## 7. Not defined here

How the core writes a record and checks its signature, how `approval-gate` checks the rule for a merge, and how a new project is set up once, before its gates are on (frame, list of signers, records branch, rules), are in the specification of GitHub and CI. Commands that create these files are in the specification of the command line. The JSON Schemas themselves are written when the formats are built.

## 8. Open

- The example field values (model, limits, paths) are illustrations; the reference project defines its own.
