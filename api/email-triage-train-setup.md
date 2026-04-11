---
name: email-triage-train-setup
type: setup
version: 1.2.0
collection: email-triage
description: Setup for the email-triage-train skill — installs the classification review and correction learning interface.
target: email-triage-train
target_type: skill
upgrade_compatible: true
---

## Setup Overview

This installs the Email Triage Train skill, which provides the iterative learning loop for improving triage accuracy. After each triage run, members can invoke this skill to review classifications, correct mistakes, and build a persistent correction history that future triage runs use.

---

## Pre-Setup Checks

- `email-triage` task is installed in the member's workspace → if not: "Install the email-triage task first — this skill reviews its classification decisions."

---

## Parameters

### `review_mode_default` [member-defined]
Default review mode when the skill is invoked.
- Options: `by-category` (recommended — bulk review grouped by category), `by-email` (one-at-a-time sequential review)
- Default: `by-category`

### `stale_log_warning_days` [member-defined]
Number of days after which the run log is considered stale and a warning is shown.
- Default: 7

---

## Setup Completion

1. Write the skill instance to the member's skills directory
2. Write `manifest.json`
3. Write `setup-responses.md` with configured parameters
4. Ensure `triage-corrections.json` exists in the email-triage task directory (created during email-triage setup, but verify)
5. Register entry in `member-index.json` with alias `@ai:email-triage-train`
6. Confirm to member: "Email Triage Train is installed. After running email-triage, say '@ai:email-triage-train' to review and improve the classifications."

---

## Upgrade Behavior

### Preserved Responses
- `review_mode_default`
- `stale_log_warning_days`
- All data in `triage-corrections.json` is preserved (managed by the email-triage task, not this setup)

### Reset on Upgrade
N/A.

### Requires Member Attention
None expected.

### Migration Notes
- v1.0 → future versions: migration notes will be added here as new versions are published.
