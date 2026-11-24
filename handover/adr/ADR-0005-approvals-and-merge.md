# ADR-0005: Approvals Are Signed by a Human Key, and Two Required Checks Protect the Merge

Status: proposed, 24 Nov 2026. Decisions D4 and D4a of the [system architecture](../system-architecture.md), with its sections on the place of the human zone and the two signing identities. Follows the [architecture principles](../principles.md).

## Requirements served

FR-022 (never merge without approval), FR-023 (an approval counts only from an authorised human), FR-032 (merge exactly the verified and approved state), FR-033 (merge only with passed evidence), SR-005 (approvers per project), SR-006 (the means of approval is not available to automatic steps), SR-024.

## Alternatives considered

| Alternative | Why not chosen |
| --- | --- |
| An approving review of the pull request on GitHub | With one account nobody may approve: the author cannot approve their own pull request, and a job may not approve (E1, tests 1.12 and 1.13). |
| One signing key for the human and the factory | The core signs its own records without a human. With the same key it could sign approvals. |
| Only the core checks the approval before it merges | The core works with the owner's GitHub account. With that account a tested but unapproved change could be merged, also in the browser. |

## Decision

1. **Approval.** An approval is a record on the records branch, committed and signed with the owner's human SSH key. It names exactly the commit it approves.
2. **Two signing identities.** The human key signs approvals, decisions and the frame. It is kept only on the owner's own machine, protected by a passphrase and not held unlocked by a key agent. The recording key of the factory signs all other records, without a human. The list of permitted signers on the default branch names every key with its role. Only a key with the human role can approve.
3. **Human zone.** Approvals and decisions are signed only on the owner's own machine. A codespace is supported for every other command. The human key is never stored in a codespace, in a secret of the platform or in a CI job.
4. **Merge.** The protection rule of the default branch requires two checks, for everyone including administrators: `verify-trusted` for the tests and `approval-gate` for an approval. `approval-gate` runs no code of the task branch. It reads the list of signers from the default branch and the records branch, and passes only if a key with the human role approved exactly the head commit. After an approval, the core starts it again by adding a label to the pull request.
5. **Checks of the core.** Before work on a project starts, the core checks that the protection rule exists. Before a merge, it checks itself that the default branch is unchanged since the verification (FR-032).

## Reasons

- A signed approval was verified without the platform. Every forged one was rejected: one without a signature, one signed with another key, one where the agent added its key to the list on its own branch, and one with a copied signature. A key with a passphrase could not be used by a step without a human (E1, tests 1.14 to 1.17).
- End to end, the owner's own account could not merge without both checks. An approval signed with the recording key of the factory did not count (E1, test 1.21). A new commit after an approval made the gate fail again (E1, test 1.23).
- Signatures, required checks and protection rules are functions of Git and GitHub. Only the check of signature and role is built (principles, rule 4). It is a building block of its own, so that a later approval in the browser (stage C) replaces only this check.

## Remaining risks

- A key that a key agent holds unlocked could be used by any process of the same user. This was not tested; the decision forbids it.
- In tests 1.21 and 1.23 both keys were throwaway keys held by a cloud session. The tests show the gate, not the protection of the key.
- If the recording key is stolen, false work orders or blockers can be written, but no approval, and no evidence without a valid attestation.
- The protection holds only while the rule requires both checks. When `approval-gate` was taken out of the rule, a change with a failed gate was merged (E1, test 1.23). The core therefore checks the rule before work starts.
- How the first list of signers of a project is established, before any approval exists, is open (SR-023).

## Accepted by

Names, date: (open)
