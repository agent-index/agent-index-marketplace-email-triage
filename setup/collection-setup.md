---
name: email-triage-collection-setup
type: collection-setup
version: 1.0.0
collection: email-triage
description: Org-admin setup for the email-triage collection — configures suggested defaults for delivery method, label prefix, categories, and priority settings that members can customize during their own setup.
upgrade_compatible: true
---

## Collection Setup Overview

This setup is run by an org admin when installing the email-triage collection. It configures suggested defaults that are offered to members as starting values during their individual setup. All settings are member-configurable — nothing is org-mandated. Members can accept the suggested defaults or pick their own values.

---

## Prerequisites

- Gmail MCP server available in the org's agent environment
- If suggesting Slack delivery: Slack MCP server available
- Org admin has confirmed that members will have access to Gmail OAuth credentials (either per-member or via a shared service account)

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

1. `collection-setup-responses.md` is written to the collection's `/setup/` directory on the remote filesystem with all suggested defaults in YAML format
2. All parameter values are valid (suggested_delivery_method is `slack` or `chat`, suggested_label_prefix is a non-empty string, suggested_max_priority_emails is a positive integer, suggested_categories contains at least one category)
3. Admin has confirmed the configuration

The responses file uses this format:

```yaml
## Email Triage Collection Configuration

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
- `suggested_delivery_method`
- `suggested_label_prefix`
- `suggested_max_priority_emails`
- `suggested_categories`

### Reset on Upgrade
N/A.

### Requires Admin Attention
- If new suggested parameters are added in a future version, the admin will be prompted to configure them.
- If the category schema changes, existing categories will be migrated where possible and the admin notified of any manual adjustments needed.

### Migration Notes
- v1.0 → future versions: migration notes will be added here as new versions are published.
