# ADR-0002: The Agent Runs with Read Rights and Hands Over a Change Package

Status: proposed, 24 Nov 2026. Decisions D1, D1a and D9 of the [system architecture](../system-architecture.md). Follows the [architecture principles](../principles.md).

## Requirements served

FR-061 (own branch per task), SR-007 (code written by the agent never has privileged access), SR-020 (protected content cannot be changed with effect), IR-003 (the agent is started automatically in a cloud environment).

## Alternatives considered

| Alternative | Why not chosen |
| --- | --- |
| The agent job holds a write token and pushes to its task branch itself | A write token is not limited to one branch. A job with `contents: write` created another branch (E1, test 1.6). |
| The agent works in a fork | A single account cannot fork its own repository (E1, test 1.5). |
| A separate CI job with a write token writes the package to the task branch | Puts a write token back into the CI service, with the same problem as the first alternative, and is not simpler. |
| The agent runs on the owner's own machine | Unattended runs outside a codespace are allowed by the instructor, and a job of the CI service is isolated from the owner's keys. On the owner's machine the agent would run next to the human signing key. |

## Decision

1. The coding agent runs in a job of GitHub Actions in the project repository. The job holds `permissions: contents: read` and nothing else.
2. When the agent has finished, the job runs `git add -A` and hands over the output of `git diff --cached --binary` against the base commit named in the work order. This is the change package.
3. The core, in the human zone, applies the package with `git apply --index` in a clean working tree at that base commit. Then it checks the resulting tree, not the text of the package: only paths on the allowlist of the task, only regular files that are not executable, nothing protected.
4. Only if the check passes does the core commit the result to the task branch.

## Reasons

- Nothing that runs code of the agent can write to the repository. The binding boundary of the threat model (SR-007) holds by construction, not by trust in the agent.
- Git applies the package. Only the check of the resulting tree is built (principles, rule 4).
- The check was tried with nine prepared packages: the honest one was accepted; a changed acceptance test, a symbolic link, an executable file, a submodule, a path with `../`, a path into `.git/hooks/`, an absolute path and a package against another base were all rejected, and nothing was written outside the working tree (E1, test 1.20).

## Remaining risks

- The tests of 1.20 ran with git 2.43.0. Another version of Git might treat a crafted package differently. The nine cases become acceptance tests of stage A, so they run with every version that is used.
- The core works on untrusted input when it applies a package. It must never execute anything from the package, for example a hook or a build step, before the check has passed.
- Whether a given coding agent can be held to read rights and still finish its work is tested per candidate in part 2 of E1 (D8).

## Accepted by

Names, date: (open)
