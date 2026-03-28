---
name: email-triage-setup
type: setup
version: 1.0.0
collection: email-triage
description: Setup for the email-triage task — configures inbox classification categories, delivery method, Gmail credentials, and priority settings.
target: email-triage
target_type: task
upgrade_compatible: true
---

## Setup Overview

This setup configures the core email triage task. It collects the member's Gmail credentials, delivery preferences, and initial classification categories. The org admin may have pre-configured default categories and delivery method at collection install time — those defaults are used as starting points but can be customized.

---

## Pre-Setup Checks

- Gmail MCP server is connected and responding (test with a simple inbox search) → if not: "Please connect a Gmail MCP server before setting up email triage."
- Gmail OAuth credentials exist at the configured path or need to be created → if not: walk the member through OAuth setup (see Prerequisites below)
- If delivery_method is `slack`: Slack MCP server is connected → if not: "Slack delivery is configured for this org but your Slack MCP isn't connected. Connect it or switch to chat delivery."

---

## Prerequisites

### Gmail OAuth Credentials

The labeling and archiving scripts require Google OAuth2 credentials with `gmail.modify` scope. Setup flow:

1. Ask the member if they already have a Google Cloud project with OAuth credentials configured for Gmail, or if they need to create one.
2. If creating new: walk through enabling the Gmail API in Google Cloud Console, creating an OAuth consent screen, and downloading `credentials.json`.
3. Ask where to store `credentials.json` and `token.json` — suggest a default path within the member's workspace.
4. **Important: first-run OAuth must be completed manually.** The scripts use `InstalledAppFlow.run_local_server()` which opens a browser for authentication. The member must run one of the scripts once from a machine with a browser (e.g., `python label_emails.py --label test --message-id dummy --dry-run --credentials-dir /path/to/creds`) to generate `token.json`. After this initial authorization, the agent can use the refresh token in headless environments.
5. Test the credentials by running the labeling script in dry-run mode.

---

## Parameters

### `delivery_method` [org-mandated]
How the triage summary is delivered after each run.
- Options: `slack`, `chat`
- Default: inherited from collection setup
- If `slack`: the member must also provide their `slack_user_id`

### `label_prefix` [org-mandated]
Prefix applied to all auto-created Gmail labels.
- Default: `ai-reviewed-`
- Example: with prefix `ai-reviewed-`, a category named `spam` gets label `ai-reviewed-spam`

### `max_priority_emails` [org-mandated]
Maximum number of high-priority emails to surface per run.
- Default: 15

### `categories` [member-overridable]
List of classification categories. Initialized from the org's `default_categories` at setup time. The member can customize via `email-triage-config` after setup.

Each category is an object with:
- `name` (string, kebab-case) — unique identifier
- `label` (string) — full Gmail label name (auto-generated from prefix + name)
- `action` (string) — `label-and-archive`, `label-only`, or `skip`
- `signals.sender_patterns` (array of strings) — email addresses or @domains
- `signals.subject_patterns` (array of strings) — subject line keywords
- `signals.description` (string) — natural language description for agent classification

During setup, present the org's default categories and ask: "These are the default categories your org has configured. Would you like to use them as-is, or customize?"

### `priority_sensitivity` [role-suggested]
How aggressively to flag emails as high priority.
- Options: `high` (1+ criteria), `medium` (2+ criteria), `low` (all 3 criteria)
- Default: `high`

### `slack_user_id` [member-defined]
The member's Slack user ID for DM delivery. Required if delivery_method is `slack`.
- Ask the member for their Slack user ID. Suggest they find it in Slack profile → three dots → "Copy member ID."

### `apps_path` [member-defined]
Path to the collection's `apps/` directory containing the `gmail-labeler` and `gmail-archiver` scripts.
- Default: resolved automatically from the collection's install directory
- Used in bash commands to invoke the labeling and archiving scripts

### `credentials_path` [member-defined]
Path to the directory containing `credentials.json` and `token.json` for Gmail OAuth.
- Default: `{member_workspace}/apps/gmail-credentials/`

### `vip_senders` [member-defined]
Email addresses or domains that always flag as high-priority.
- Default: empty array
- Ask: "Are there any senders whose emails should always be flagged as high priority? (e.g., your manager, key clients)"

### `ignore_senders` [member-defined]
Email addresses or domains that always classify as spam.
- Default: empty array
- Ask: "Are there any senders whose emails should always be treated as spam?"

---

## Setup Completion

1. Write `setup-responses.md` to the member's task directory with all configured parameters in YAML format
2. Write `manifest.json` to the member's task directory
3. Create empty `triage-corrections.json` with the base schema
4. Create empty `triage-run-log.json` placeholder
5. Test Gmail credentials by running `label_emails.py --dry-run` with a dummy label
6. Register entry in `member-index.json` with alias `@ai:email-triage`
7. Confirm to member: "Email Triage is set up with {N} categories. Say '@ai:email-triage' to run it, or '@ai:email-triage-config' to adjust your categories."

---

## Upgrade Behavior

### Preserved Responses
- `categories` (including any member customizations)
- `slack_user_id`
- `credentials_path`
- `vip_senders`
- `ignore_senders`
- `priority_sensitivity`
- `triage-corrections.json` (all training data preserved)

### Reset on Upgrade
- `triage-run-log.json` (ephemeral, overwritten each run anyway)

### Requires Member Attention
- If new org-mandated parameters are added in a future version, the member may be prompted to review them
- If the category schema changes, existing categories will be migrated automatically where possible

### Migration Notes
- v1.0 → future versions: migration notes will be added here as new versions are published.
