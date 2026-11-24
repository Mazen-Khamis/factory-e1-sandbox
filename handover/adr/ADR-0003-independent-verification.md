# ADR-0003: The Verification Runs from the Definition on the Default Branch

Status: proposed, 24 Nov 2026. Decisions D2 and D2a of the [system architecture](../system-architecture.md). Follows the [architecture principles](../principles.md).

## Requirements served

FR-080 (verification in an independent environment), FR-081 (evidence bound to the approved tests and the exact state), SR-007, SR-020, SR-021 (verification in a run the agent does not control), IR-042 (GitHub Actions as verification environment).

## Alternatives considered

| Alternative | Why not chosen |
| --- | --- |
| Verification started by the event `pull_request` | The definition and the tests of the task branch run. A changed definition ran no test and reported success (E1, test 1.2). |
| Verification started with `gh workflow run` from the default branch | Runs the right definition (E1, test 1.18), but its check belongs to the commit of the default branch, not to the pull request, so it cannot be a required check of the merge. Kept only for repeating a verification. |
| `pull_request` for the tests and a second, trusted workflow (`workflow_run`) that reports the result | Its check also belongs to the default branch, and it adds a second workflow and a way to hand the result over. Not simpler. |

## Decision

1. The core opens the pull request of the task branch. The agent cannot, because it holds read rights only.
2. Opening it starts the workflow `verify-trusted` through `pull_request_target`, with the workflow definition of the default branch. The workflow checks out the default branch and the head of the pull request separately, copies the approved acceptance tests over those of the task branch, and runs them against the code of the task branch.
3. What the trusted workflows may do (D2a):
   - `permissions: contents: read` only: no secret, no `id-token`, no write right;
   - every checkout with `persist-credentials: false`, and `allow-unsafe-pr-checkout` left at its default `false`;
   - the attestation in a job of its own, which executes no code of the task branch and alone holds `id-token: write` and `attestations: write` (see [ADR-0004](ADR-0004-evidence-by-attestation.md));
   - an Actions event policy of the project repository allows `pull_request_target` and `workflow_dispatch` only for `verify-trusted.yml` and `approval-gate.yml`.
4. A run that the platform blocks counts as a blocker, never as passed.

## Reasons

- The definition and the tests of the approved state ran, the changes of the task branch had no effect and were detected (E1, tests 1.3 and 1.18).
- Code under test found no credential and could not write (E1, test 1.4).
- The run is the required check of the merge, attached to the head of the pull request (E1, tests 1.6 and 1.21).
- GitHub blocks `pull_request_target` in public repositories by default from 2 Dec 2026, unless an Actions event policy allows it. The policy is the mechanism GitHub provides for this case (principles, rule 1).

## Remaining risks

- That the event policy keeps both workflows running once the default block is in force can only be shown from 2 Dec 2026 (E1, test 1.24). Until then this decision holds with that condition. If it fails, the checks stop with an error, and nothing counts as verified.
- `pull_request_target` remains a trigger that GitHub warns about. The decision is safe only as long as the conditions of point 3 hold. A change to either trusted workflow is a change of protected content.
- The code under test is not isolated from the test harness at run time. This is accepted in the [risk decision](ADR-0001-risk-acceptance-code-under-test.md).

## Accepted by

Names, date: (open)
