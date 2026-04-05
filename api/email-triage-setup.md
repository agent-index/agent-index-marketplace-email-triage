---
name: email-triage-setup
type: setup
version: 1.0.0
collection: email-triage
description: Setup for the email-triage task — configures inbox classification categories, delivery method, Gmail credentials, and priority settings. All parameters are member-defined; collection setup provides suggested defaults as starting values.
target: email-triage
target_type: task
upgrade_compatible: true
---

## Setup Overview

This setup configures the core email triage task. It collects the member's Gmail credentials, delivery preferences, and initial classification categories. The org admin may have configured suggested defaults at collection install time — those are offered as starting values but the member owns all settings and can change any of them.

---

## Pre-Setup Checks

- Gmail MCP server is connected and responding (test with a simple inbox search) → if not: "Please connect a Gmail MCP server before setting up email triage."
- Org-level `credentials.json` exists on the remote filesystem (read from `gmail_credentials_path` in `collection-setup-responses.md` using `aifs_read`) → if not: "Your org admin needs to complete the collection setup first — it provides the Gmail OAuth credentials that all members use. Contact your admin."
- If delivery_method is `slack`: Slack MCP server is connected → if not: "You've chosen Slack delivery but your Slack MCP isn't connected. Connect it or switch to chat delivery."

---

## Prerequisites

### Gmail Authorization

The labeling and archiving scripts require a personal `token.json` that authorizes your Gmail account. Your org admin has already provided the OAuth app credentials (`credentials.json`) at collection install time — you just need to authorize your account against it.

**Setup flow:**

1. Copy `credentials.json` from the remote filesystem (`gmail_credentials_path` in collection setup responses) to the member's **local** token directory: `{member_workspace}/apps/gmail-credentials/credentials.json` (using `aifs_read` → native Write).
2. **Run the browser authorization flow.** The member must run the labeling script once from a machine with a browser to generate their personal `token.json`:
   ```
   python label_emails.py --label test --message-id dummy --dry-run \
       --credentials-file {member_workspace}/apps/gmail-credentials/credentials.json \
       --token-dir {member_workspace}/apps/gmail-credentials/
   ```
   This opens a browser window where the member clicks "Allow" to authorize their Gmail account. After this one-time step, the agent can use the refresh token in headless environments.
3. Test the credentials by running the labeling script in dry-run mode.
4. Once `token.json` is generated, the local copy of `credentials.json` can optionally be removed — it's only needed for the initial authorization and token refresh. Keeping it avoids re-fetching if the token expires and needs re-authorization.

> **What members DON'T need to do:** Create a Google Cloud project, enable APIs, configure OAuth consent screens, or download credentials. The admin handled all of that.

---

## Parameters

### `delivery_method` [member-defined]
How the triage summary is delivered after each run.
- Options: `slack`, `chat`
- Suggested default: from collection setup's `suggested_delivery_method` (typically `slack`)
- Ask: "How would you like triage summaries delivered? Options: 'slack' (sends a DM) or 'chat' (outputs in conversation). Your org suggests '{suggested_delivery_method}'."
- If `slack`: the member must also provide their `slack_user_id`

### `label_prefix` [member-defined]
Prefix applied to all auto-created Gmail labels.
- Suggested default: from collection setup's `suggested_label_prefix` (typically `ai-reviewed-`)
- Ask: "What prefix should be used for Gmail labels? Suggested: '{suggested_label_prefix}'. For example, a category named 'spam' gets label '{suggested_label_prefix}spam'."
- Example: with prefix `ai-reviewed-`, a category named `spam` gets label `ai-reviewed-spam`

### `max_priority_emails` [member-defined]
Maximum number of high-priority emails to surface per run.
- Suggested default: from collection setup's `suggested_max_priority_emails` (typically `15`)
- Ask: "How many high-priority emails should be surfaced per run? Suggested: {suggested_max_priority_emails}."

### `categories` [member-defined]
List of classification categories. Initialized from the collection setup's `suggested_categories` as a starting point. The member can customize during setup and anytime after via `email-triage-config`.

Each category is an object with:
- `name` (string, kebab-case) — unique identifier
- `label` (string) — full Gmail label name (auto-generated from prefix + name)
- `action` (string) — `label-and-archive`, `label-only`, or `skip`
- `signals.sender_patterns` (array of strings) — email addresses or @domains
- `signals.subject_patterns` (array of strings) — subject line keywords
- `signals.description` (string) — natural language description for agent classification

During setup, present the suggested categories and ask: "These categories are suggested as a starting point. Would you like to use them as-is, customize them, or start fresh with your own?"

### `priority_sensitivity` [member-defined]
How aggressively to flag emails as high priority.
- Options: `high` (1+ criteria), `medium` (2+ criteria), `low` (all 3 criteria)
- Default: `high`
- Ask: "How aggressively should emails be flagged as high priority? 'high' (flag if any one criterion is met), 'medium' (two or more), or 'low' (all three). Default is 'high'."

### `slack_user_id` [member-defined]
The member's Slack user ID for DM delivery. Required if delivery_method is `slack`.
- Ask the member for their Slack user ID. Suggest they find it in Slack profile → three dots → "Copy member ID."

### `apps_path` [member-defined]
Path to the collection's `apps/` directory containing the `gmail-labeler` and `gmail-archiver` scripts.
- Default: resolved automatically from the collection's install directory
- Used in bash commands to invoke the labeling and archiving scripts

### `token_dir` [member-defined]
Path to the directory where the member's personal `token.json` is stored (generated during the browser auth flow in Prerequisites).
- Default: `{member_workspace}/apps/gmail-credentials/`
- Note: `credentials.json` is provided org-wide by the admin (see collection setup). It is copied to this directory during member setup to support the initial auth flow and token refresh.

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
5. Test Gmail credentials by running `label_emails.py --dry-run --credentials-file {token_dir}/credentials.json --token-dir {token_dir}` with a dummy label
6. Register entry in `member-index.json` with alias `@ai:email-triage`
7. Confirm to member: "Email Triage is set up with {N} categories. Say '@ai:email-triage' to run it, or '@ai:email-triage-config' to adjust your categories."

---

## Upgrade Behavior

### Preserved Responses
- `categories` (including any member customizations)
- `slack_user_id`
- `token_dir`
- `vip_senders`
- `ignore_senders`
- `priority_sensitivity`
- `triage-corrections.json` (all training data preserved)

### Reset on Upgrade
- `triage-run-log.json` (ephemeral, overwritten each run anyway)

### Requires Member Attention
- If new parameters are added in a future version, the member will be prompted to configure them
- If the category schema changes, existing categories will be migrated automatically where possible

### Migration Notes
- v1.0 → future versions: migration notes will be added here as new versions are published.
