# ADR-0007: Claude Code and Codex Are the Coding Agents, with the Owner's Subscriptions

Status: proposed, 24 Nov 2026. Decision D8 of the [system architecture](../system-architecture.md). Changes [ADR-0002](ADR-0002-agent-execution-and-change-package.md), decision point 1, as far as the credential is concerned. Follows the [architecture principles](../principles.md).

## Context

The owner decided on 24 Nov 2026 that the factory is built for his own use, not for others, and that it uses the coding agents he already has access to: Claude Code and Codex, each with his own subscription. OpenRouter, OpenHands and OpenCode are no longer candidates.

Part 2 of experiment E1 ran both agents unattended in a job with read rights only (`docs/05-evaluation/experiments/E1-results-part-2.md`).

## Requirements served

IR-001 to IR-008 (adapter interface), IR-003 (one adapter in stage A), DR-021 (provenance of a run), SR-001 (no secret in the repository, records, frontend or logs), SR-007 (no privileged access for code of the agent).

The decision conflicts with three approved requirements, which must be changed first (see "Open before acceptance"): IR-040 (OpenRouter), SR-008 (a dedicated key with a spending limit), and, for stage B, FR-143 (cost per model call matched to the provider's bill).

## Alternatives considered

| Alternative | Why not chosen |
| --- | --- |
| OpenRouter with an API key, as IR-040 requires | Pays per token in addition to the subscriptions the owner already has. Not needed for use by the owner alone. |
| OpenHands Software Agent SDK | Open source, but needs an API key of a model provider and pays per token; it cannot use the owner's subscriptions. |
| OpenCode | Removed by the owner on 24 Nov 2026. |
| API keys for Anthropic and OpenAI instead of subscriptions | Gives real cost per run and a spending limit per key, but pays per token. Stays possible later through the same adapters. |
| Codex in a public repository with the subscription login | OpenAI advises against it. The run showed why: GitHub masks a multi-line secret line by line, so a token printed alone would not be masked (E1, part 2). |

## Decision

1. **First adapter, stage A: Claude Code**, started as `claude -p` with JSON output, a limit of turns, and an explicit list of allowed tools. Its access is the secret `CLAUDE_CODE_OAUTH_TOKEN` of the project repository, made by the owner with `claude setup-token`. Claude Code is officially supported in this form and works in public and private repositories.
2. **Second adapter, after stage A: Codex**, started as `codex exec --json --sandbox workspace-write`. Its access is the owner's `auth.json` from `codex login`, as a secret of the project repository, written by the job to a folder outside the working tree, readable only by the job's user, and removed at the end, also when the job fails. This file is not one of the places SR-001 names; it is never staged, uploaded as an artifact or printed. **Only in private repositories.** It is the proof that the adapter interface is not bound to one agent (G6, IR-002). The Codex adapter is built only when the renewal of its login is solved (point 7).
3. **Model.** The adapter always sets the model explicitly (`--model`) and records it as a parameter of the run. The run record also states the model the agent reported: Claude Code reports it; Codex does not, so for Codex it is recorded as "not reported" (DR-021).
4. **Usage.** The run record keeps the tokens the agent reports and, for Claude Code, its estimated cost, marked as an estimate. A subscription is not billed per run, so no cost per run is matched to a bill.
5. **Credential (changes ADR-0002, point 1).** The only credential in the agent job besides its read-only `GITHUB_TOKEN` is the access of the agent's subscription. It is never printed, never stored in a public repository for Codex, and revoked when it may have been exposed. The code that the agent runs in the same job can read it; this is accepted as a risk by the owner (see "Risk accepted").
6. **Limits.** Three things are kept apart:
   - **Limits of the factory:** time per run, turns per run, number of runs per task. The factory enforces them.
   - **Financial limit:** paid usage beyond the subscription stays switched off at both providers. The owner checks this before the first real run and after every change of plan.
   - **Misuse of a credential:** the limits of a subscription renew, so a stolen credential could be misused over several periods. This is not bounded by the factory; it is part of the risk accepted below and is ended only by revoking the credential.
7. **Renewal of the Codex login.** The agent job never gets a right to write to the secret store. How an exchanged refresh token gets back into the secret store, by a separate step without agent code, by a new login of the owner, or by another login that OpenAI supports, is decided before the Codex adapter is built.
8. **Repositories.** A project that uses Codex is a private repository. On GitHub Free a private repository has no rulesets and no branch protection, so ADR-0005 and ADR-0006 cannot be enforced there; such a project needs GitHub Pro. Before the first private Codex project, the needed rules are tried in a private repository with that plan. A project that uses only Claude Code may be public.

## Reasons

- Both agents passed part 2 of E1: they started without interaction, ended by themselves, changed only the allowed file, made no commit, could not write with what the job holds, did not leave their access anywhere the check looked, and their package passed the check of the core.
- The owner already pays for both subscriptions, so model use costs nothing extra (principles, rule 1). This is not a claim that subscriptions are safer or cheaper in general: they move effort and risk from cost to authentication, protection of the account and quotas. GitHub Actions minutes and, for private projects, GitHub Pro still cost money.
- Supporting Claude Code and Codex through the same adapter contract will show that the interface is agent-neutral (G6) once both adapters pass the conformance tests of the contract. Part 2 of E1 shows only that both agents can be run this way.

## Remaining risks

- **Personal credentials.** Both credentials belong to the owner's personal accounts. If one is exposed, someone else uses the owner's subscription until it is revoked. Codex's `auth.json` is the owner's login itself, not a separate key; revoking it logs the owner out everywhere. A private repository does not protect against the code in the job; it only keeps the logs from the public.
- **Codex login over time.** The refresh token in `auth.json` can be exchanged during use. In the test it was not. Point 7 makes this a condition of the Codex adapter.
- **Cost.** Without a bill per run, a budget per project (FR-144, stage B) can only be kept in tokens or in runs, not in money.
- **Terms of use.** Anthropic documents the subscription token for CI. OpenAI documents the subscription login for CI as "advanced" and only for private repositories. If either provider changes this, the adapter switches to an API key, and IR-040 and SR-008 apply in their changed form.
- **Not tested:** a run that reaches its time or turn limit; a larger or failing task; an agent that tries to change a protected file. These become acceptance tests of stage A.

## Risk accepted

The owner accepts that the access of his subscriptions is present in a job in which the coding agent runs code, and that such code can read it. The alternative that bounds this risk better is an API key with a spending limit for each provider; it stays available through the same adapters if this acceptance is withdrawn.

Accepted by the owner: (name, date)

## Open before acceptance

Change records in `docs/02-requirements/changes.md`, each approved by the owner:

- **IR-040:** replace "through OpenRouter as the first model provider" by: the agent uses the access configured by its user; provider, requested model, reported model and usage are recorded per run as reported, and an item that is not reported is recorded as such.
- **SR-008:** replace "a dedicated key with a spending limit" by: a credential that is dedicated to the factory where the provider allows it and can be revoked; paid usage beyond a subscription is switched off; the factory limits time, turns and runs; misuse of a subscription credential that these do not bound is a risk accepted by the owner in a decision record.
- **FR-143 and FR-144** (stage B): to be changed before stage B starts, so that usage is logged in tokens and a budget may be set in tokens or runs.

## Accepted by

Names, date: (open)
