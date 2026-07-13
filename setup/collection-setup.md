---
name: email-triage-collection-setup
type: collection-setup
version: 1.2.0
collection: email-triage
description: Org-admin setup for the email-triage collection — configures suggested defaults for delivery method, label prefix, categories, and priority settings that members can customize during their own setup.
upgrade_compatible: true
---

## Collection Setup Overview

This setup is run by an org admin when installing the email-triage collection. It handles two things: (1) providing the org's Gmail OAuth credentials that all members authenticate against, and (2) configuring suggested defaults for delivery method, labels, and categories. The OAuth credentials are org-mandated; the suggested defaults are fully member-configurable.

---

## Prerequisites

- Gmail MCP server available in the org's agent environment
- If suggesting Slack delivery: Slack MCP server available
- Access to a Google Cloud project with the Gmail API enabled (admin will provide the OAuth `credentials.json` during setup below)

---

## Org-Level Credential Setup

### `gmail_credentials_json` [org-mandated]

The Gmail labeling and archiving scripts require a Google Cloud OAuth2 `credentials.json` file (the OAuth app identity). This is an org-level artifact — individual members do not create their own Google Cloud projects. Members only authorize their own Gmail account against this shared OAuth app during their member setup.

**Setup flow:**

1. Ask the admin: "Do you already have a Google Cloud project with an OAuth client configured for the Gmail API (`gmail.modify` scope), or do you need to create one?"
2. If creating new: walk through enabling the Gmail API in Google Cloud Console, creating an OAuth consent screen (internal to the org), creating a Desktop OAuth client ID, and downloading `credentials.json`.
3. Store `credentials.json` on the **remote filesystem** at: `org-config/apps/gmail-credentials/credentials.json` (using `aifs_write`).
4. Confirm: "This credentials.json will be used by all members for email labeling and archiving. Each member will authorize their own Gmail account against it during their setup."

> **Why org-level?** The `credentials.json` identifies the OAuth app (a Google Cloud project artifact). Creating one requires Google Cloud Console access, billing awareness, and org-level decisions about consent screen branding. Members shouldn't need to know any of this — they just click "Allow" in a browser during their setup.

---

## Suggested Default Parameters

These are the starting values offered to members during their setup. Members can accept, modify, or replace any of them.

### `suggested_delivery_method`
How triage summaries are delivered to members.
- Options: `slack`, `chat`
- Ask: "What delivery method should be suggested to members? Options: 'slack' (sends a DM after each run) or 'chat' (outputs directly in the conversation). Members can choose a different method during their own setup."
- If `slack`: note that members will need a connected Slack MCP server.

### `suggested_label_prefix`
Suggested prefix for auto-created Gmail labels.
- Default: `ai-reviewed-`
- Ask: "What label prefix should be suggested to members? Default is 'ai-reviewed-' (creates labels like 'ai-reviewed-spam', 'ai-reviewed-news'). Members can change this."

### `suggested_max_priority_emails`
Suggested maximum number of high-priority emails surfaced per run.
- Default: 15
- Ask: "What max priority count should be suggested? Default is 15. Members can adjust this."

### `suggested_categories`
The starter set of classification categories offered to members at setup time. Members can customize, add, or remove categories during their own setup and anytime after via `email-triage-config`.

Present the built-in defaults and ask the admin to confirm, modify, or extend:

**Built-in defaults:**

```yaml
- name: spam
  label: "{label_prefix}spam"
  action: label-and-archive
  signals:
    sender_patterns: []
    subject_patterns: []
    description: >
      Unsolicited, promotional, or junk email. Marketing blasts, sales offers,
      bulk-send messages, no-reply senders with no meaningful content.

- name: news
  label: "{label_prefix}news"
  action: label-and-archive
  signals:
    sender_patterns: []
    subject_patterns: []
    description: >
      Industry newsletters, articles, blog posts, research papers, or curated
      reading lists. Content to be read for professional awareness, not
      notifications about accounts or services.

- name: notices
  label: "{label_prefix}notices"
  action: label-and-archive
  signals:
    sender_patterns: []
    subject_patterns: []
    description: >
      Operational or legal notifications from services and platforms.
      Terms of service updates, billing notices, security alerts,
      service status updates, automated platform notifications.
      Exception: calendar acceptances or declines from real people
      should be classified as 'other'.
```

Ask: "These are the default categories that will be suggested to members. Would you like to add any org-specific categories? For example, categories for specific vendor notifications, internal tool alerts, or recurring report types. Members can always add their own categories later."

For each additional category the admin wants to add, collect: name, description, sender patterns (optional), subject patterns (optional), and action.

---

## Setup Completion

Collection setup is complete when:

1. `credentials.json` is stored on the remote filesystem at `org-config/apps/gmail-credentials/credentials.json` (using `aifs_write`)
2. `collection-setup-responses.md` is written to the collection's `/setup/` directory on the remote filesystem with all suggested defaults in YAML format
3. All parameter values are valid (suggested_delivery_method is `slack` or `chat`, suggested_label_prefix is a non-empty string, suggested_max_priority_emails is a positive integer, suggested_categories contains at least one category)
4. Admin has confirmed the configuration

The responses file uses this format:

```yaml
## Email Triage Collection Configuration

gmail_credentials_path: "org-config/apps/gmail-credentials/credentials.json"
suggested_delivery_method: slack
suggested_label_prefix: "ai-reviewed-"
suggested_max_priority_emails: 15

suggested_categories:
  - name: spam
    label: ai-reviewed-spam
    action: label-and-archive
    signals:
      sender_patterns: []
      subject_patterns: []
      description: >
        Unsolicited, promotional, or junk email.

  - name: news
    label: ai-reviewed-news
    action: label-and-archive
    signals:
      sender_patterns: []
      subject_patterns: []
      description: >
        Industry newsletters, articles, and professional reading content.

  - name: notices
    label: ai-reviewed-notices
    action: label-and-archive
    signals:
      sender_patterns: []
      subject_patterns: []
      description: >
        Operational notifications from services and platforms.
```

---

## Upgrade Behavior

### Preserved Responses
- `gmail_credentials_path`
- `suggested_delivery_method`
- `suggested_label_prefix`
- `suggested_max_priority_emails`
- `suggested_categories`

### Reset on Upgrade
N/A.

### Requires Admin Attention
- If new suggested parameters are added in a future version, the admin will be prompted to configure them.
- If the category schema changes, existing categories will be migrated where possible and the admin notified of any manual adjustments needed.

### Requires Member Attention
None for PATCH/MINOR upgrades. MAJOR version upgrades will document required member actions here.

### Migration Notes
- v1.0 → future versions: migration notes will be added here as new versions are published.
