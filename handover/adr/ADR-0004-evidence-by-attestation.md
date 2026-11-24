# ADR-0004: Evidence Is a Result File with a Signed Attestation

Status: proposed, 24 Nov 2026. Decision D3 of the [system architecture](../system-architecture.md). Follows the [architecture principles](../principles.md).

## Requirements served

FR-081 (evidence bound to the exact state and the approved tests), DR-022 (what evidence records), DR-025 (evidence stays valid without the system that produced it), SR-007, SR-024 (origin and integrity of a record can be verified).

## Alternatives considered

| Alternative | Why not chosen |
| --- | --- |
| The result of the run on the platform is the evidence | Runs and logs are gone after 90 days at most (E1, test 1.10), and checking them needs the platform. |
| The verification job writes the evidence record itself | That job runs code of the agent and must hold no write right (SR-007). |
| The core signs the result with the recording key of the factory | Proves only that the core wrote it, not that it came from the trusted run. |

## Decision

1. The verification job writes a result file. It names the state of the approved acceptance tests, the state of the task branch and the run.
2. A separate job, which executes no code of the task branch, creates a signed attestation of this file with `actions/attest-build-provenance`.
3. The core verifies the attestation, and checks that the three states in the file match the work order and the approval.
4. The core writes the evidence record to the records branch, with the result file, the bundle of the attestation and the trusted root.

## Reasons

- The attestation names the workflow file on the default branch, the commit, the trigger and the run. It was verified later with the saved file, bundle and trusted root, and a changed file failed (E1, test 1.9).
- Attestations are a function of the platform. Only the check of the three states is built (principles, rule 4).

## Remaining risks

- A valid attestation proves where a result comes from. It does not prove that the tests are correct or complete, and it does not prove that the code under test could not influence the result (see the [risk decision](ADR-0001-risk-acceptance-code-under-test.md)).
- The result file is written in the job that runs the code under test. The attestation proves the origin of the file, not that the code could not change it before it was attested.
- The test of 1.9 ran in a public repository, and the network was not cut during the later verification.

## Accepted by

Names, date: (open)
