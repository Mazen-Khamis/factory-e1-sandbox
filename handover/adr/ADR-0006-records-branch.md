# ADR-0006: Records Are Kept on a Protected Branch of Their Own

Status: proposed, 24 Nov 2026. Decision D5 of the [system architecture](../system-architecture.md). Follows the [architecture principles](../principles.md).

## Requirements served

DR-001 (everything of a project is kept in its repository), DR-024 and DR-026 (work orders and run records in the project repository), DR-027 (blockers are records), SR-024 (origin and integrity of a record can be verified), and the definition of a record in [03-data.md](../../02-requirements/03-data.md): written once and not changed afterwards.

## Alternatives considered

| Alternative | Why not chosen |
| --- | --- |
| A folder on the default branch, each record through a pull request | The default branch accepts changes only through a pull request with passed checks ([ADR-0005](ADR-0005-approvals-and-merge.md)). Every work order, blocker and approval would need a pull request and a verification run of its own; a blocker after a failed run could not wait for one. |
| Records on the task branch | Lost with the task branch; violates DR-001. |
| A database outside the repository | Against P1: the project repository is the single source of truth. Not needed in stage A. |

## Decision

1. Records are kept on a branch of their own in the project repository. Only the core writes to it.
2. A ruleset protects the branch, without a bypass: "Restrict deletions", "Block force pushes" and "Require linear history".
3. Whenever the core reads the branch, it checks that every commit only adds files (`git log --diff-filter=MDR` finds nothing) and that no commit is a merge. Otherwise the records count as damaged, and the factory stops with a blocker.
4. Every commit on the branch is signed: with the human key for approvals, decisions and the frame, and with the recording key of the factory for all other records. The core checks signature and role.
5. Records refer to states of the default branch and of the task branch by their identifiers (DR-005).

## Reasons

- Records are written at once, also when nothing was verified. The default branch stays as protected as it is.
- The ruleset refused deletion, force push and merge commits, also for the owner, while a normal push succeeded (E1, tests 1.19 and 1.22).
- Rulesets are a function of GitHub. Only the check for growth and origin is built (principles, rule 4).

## Remaining risks

- The ruleset does not make the branch append only: a normal commit that changes or deletes a record was accepted (E1, test 1.19). The check of point 3 closes this gap. If the check is skipped, a changed record goes unnoticed.
- The owner can change or remove the ruleset. The core cannot prevent this, but its check of point 3 notices the effect.

## Accepted by

Names, date: (open)
