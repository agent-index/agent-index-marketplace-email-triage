---
name: email-triage-config-setup
type: setup
version: 1.0.0
collection: email-triage
description: Setup for the email-triage-config skill — installs the interactive category management interface.
target: email-triage-config
target_type: skill
upgrade_compatible: true
---

## Setup Overview

This installs the Email Triage Config skill, which provides interactive management of triage categories, VIP senders, ignore lists, and priority settings. This skill operates on the same `setup-responses.md` file used by the `email-triage` task.

---

## Pre-Setup Checks

- `email-triage` task is installed in the member's workspace → if not: "Install the email-triage task first — this skill manages its configuration."

---

## Parameters

No additional member-configurable parameters. This skill reads and writes to the email-triage task's `setup-responses.md`.

---

## Setup Completion

1. Write the skill instance to the member's skills directory
2. Write `manifest.json`
3. Write empty `setup-responses.md` (stub — the skill operates on the email-triage task's config)
4. Register entry in `member-index.json` with alias `@ai:email-triage-config`
5. Confirm to member: "Email Triage Config is installed. Say '@ai:email-triage-config' to manage your categories and sender lists."

---

## Upgrade Behavior

### Preserved Responses
N/A — this skill has no parameters of its own.

### Reset on Upgrade
N/A.

### Requires Member Attention
None expected.

### Migration Notes
- v1.0 → future versions: migration notes will be added here as new versions are published.
