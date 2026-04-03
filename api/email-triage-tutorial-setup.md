---
name: email-triage-tutorial-setup
type: setup
version: 1.2.0
collection: email-triage
description: Setup for the email-triage-tutorial skill — minimal setup that only requires access to the member's configuration to provide personalized examples.
target: email-triage-tutorial
target_type: skill
upgrade_compatible: true
---

## Setup Overview

The email-triage tutorial is a reference skill that explains the collection's concepts and workflows. It doesn't perform operations or modify configuration — it only reads and explains. Setup is minimal: the skill just needs access to read the member's existing email-triage setup responses so it can use their actual categories and settings in examples.

---

## Pre-Setup Checks

- Member has completed setup for the core `email-triage` task → if not: "Please set up the email-triage task first. The tutorial will be more useful once your categories and settings are configured."

---

## Parameters

No parameters are required for the tutorial skill. It reads the member's `setup-responses.md` file for the `email-triage` task at runtime to provide personalized examples.

---

## Setup Completion

1. Register entry in `member-index.json` with alias `@ai:email-triage-tutorial`
2. Confirm to member: "Email Triage tutorial is ready. Say '@ai:email-triage-tutorial' to get a guided tour of the collection, or ask a specific question about how something works."

---

## Upgrade Behavior

No state is preserved or reset — the skill has no member-specific configuration. Upgrades are transparent.
