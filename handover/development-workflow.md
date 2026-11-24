# Development Workflow

Status: Draft 2, 24 Nov 2026. How the factory itself is developed in this repository. The rules that must hold are in [rules-from-requirements.md](rules-from-requirements.md); this file says how the work is done. Coding agents read it through [AGENTS.md](../../AGENTS.md).

## 1. Who does what

| Role | Who | Does | Never |
| --- | --- | --- | --- |
| Owner | Mazen Khamis | Decides; approves requirements, changes and decision records; records manual verifications; merges; pushes the default branch | – |
| Coding agent | Claude Code or Codex on the owner's machine, in the devcontainer | Writes code, tests and documents from a prompt, on a branch of a work package | Pushes the default branch; merges; changes `approvals.md` or `verification.md`; accepts a decision |
| Assistant | Claude in claude.ai | Writes specifications, plans and prompts; reviews pull requests (section 3, step 8); writes parts of the code when the owner asks | The same as the coding agent |
| Second reviewer | another AI tool, chosen by the owner | Reviews documents and decisions on request | – |

Everything any AI writes reaches the default branch through a pull request that the owner merges.

**Credentials.** A coding agent works in the devcontainer without access to the owner's human signing key, the recording key of the factory, or any credential that permits privileged operations on a repository. The devcontainer mounts no SSH keys, and forwarding of the SSH agent and of Git credentials from the host is switched off. The agent commits on its branch without signing; pushing, signing, approving and merging are done by the owner outside the agent's session (ADR-0005). Every session in which an AI changes the repository gets a row in [docs/ai-use-log.md](../ai-use-log.md).

## 2. Work packages

The work of a stage is cut into work packages under [docs/06-backlog/](../06-backlog/). Each package names:

- the requirements it fulfils, by ID;
- the specification it implements, if any;
- the tests that show it, and for each the requirement it verifies;
- what is out of the package.

A package is small enough for one pull request. A package that grows is split, not stretched.

## 3. From package to merge

1. **Branch.** One branch per package, named `wp/<NN>-<short-name>`, for example `wp/02-record-formats`, made from the current default branch.
2. **Specification first.** If the package needs a specification that does not exist, it is written and reviewed before code is written.
3. **Tests first.** The tests of the package are written before or together with the code. Each test names the requirement it verifies (section 4).
4. **Code.** Small commits with messages in English that say what changed and why.
5. **Locally green.** All tests pass in the devcontainer before the pull request is opened.
6. **Pull request.** Title: the package. Description: the requirements covered, the tests added, what is open, and every point where the specification was unclear and the reading chosen.
7. **CI.** The workflow `tests` runs on every pull request (section 5).
8. **Review.** The assistant reviews the pull request against the specification and the requirements: it reads the branch when the repository is attached to its session, otherwise the owner gives it the diff. The owner puts the findings into the pull request and decides. A change that touches only wording of documents, with no requirement, decision or code affected, may be merged without this review.
9. **Merge.** The owner merges only a pull request whose checks are green and whose review findings are resolved or accepted.
10. **Verification records.** Requirements verified by inspection, demonstration or measurement are recorded by the owner in [verification.md](../02-requirements/verification.md). Until the tool of section 4 exists, the owner also records there, for each merged package, the commit, the CI run, its result and the requirement IDs its tests name; this is an interim record, because the report of a CI run is kept by GitHub for a limited time only.

A package is done when it is merged, its tests pass on the default branch, its manual verifications are recorded, and the documents it affects are updated.

## 4. Tests name their requirement

The overview of the requirements says: the test names the requirement ID, the run names the commit, and the test report is the evidence. In this repository:

- A test that verifies a requirement carries the marker `@pytest.mark.req("FR-007")`; one test may name several IDs.
- A test that verifies no requirement by itself, for example of a helper, carries `@pytest.mark.support`.
- A test without either marker fails the run. Both markers are registered in `pyproject.toml`, and a small hook in `tests/conftest.py` checks at collection that every test has one of them and that every ID given to `req` has the form of a requirement ID.
- CI writes a JUnit report. Together with the commit of the run it is the evidence of the requirements the tests name; the tool that turns it into verification records is a later package.

## 5. CI of this repository

- One workflow, `tests`, on every push to a branch and on every pull request: it installs the package with its development dependencies in the image of the devcontainer and runs pytest with the JUnit report.
- A second job, `protected-files`, detects a pull request that changes `docs/02-requirements/approvals.md` or `docs/02-requirements/verification.md`, or sets a decision record to "accepted", and fails. The owner makes these changes in his own commits outside pull requests. On this private repository on GitHub Free, the owner enforces the rule by looking at the check before merging: a procedural control, not a restriction the repository enforces (rule 4 of [rules-from-requirements.md](rules-from-requirements.md); section 7).
- A pull request that changes a file under `.github/workflows/` is marked by `protected-files` for the owner's attention, because it could change the checks themselves.
- No secret is used by the CI of this repository.

## 6. Dependencies and environment

- The supported environment is the devcontainer (IR-043). The coding agent works inside it.
- A new dependency is added only with a reason in the pull request, with a lower version bound in `pyproject.toml`, and with a licence that allows use in this project.
- Generated files are changed through their source and their generator. Files that are maintained by hand, including a schema that is itself the definition, are edited directly. The schemas under `schemas/` are generated by `tools/make_schemas.py` for now.

## 7. Limits of this workflow

- This repository is private on GitHub Free. Its default branch cannot be protected, so a red check does not stop a merge; the owner does. With a paid plan, `tests` and `protected-files` would become required checks.
- `protected-files` cannot tell a commit of the owner from one of an agent outside a pull request. It protects the path through pull requests, not every push.
- The devcontainer is not a security boundary against the owner's machine. The rule on credentials in section 1 keeps privileged credentials out of the agent's reach; it does not isolate the agent from everything else on the machine.

## Open

- Confirmation of the roles in section 1 by the owner.
- Whether the owner moves to a paid GitHub plan, so that the checks of section 5 become required.
