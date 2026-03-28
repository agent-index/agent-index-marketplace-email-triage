---
name: email-triage-collection-setup
type: collection-setup
version: 1.0.0
collection: email-triage
description: Org-admin setup for the email-triage collection — configures delivery method, label prefix, and default categories for all members.
upgrade_compatible: true
---

## Collection Setup Overview

This setup is run by an org admin when installing the email-triage collection. It configures org-wide defaults that flow into every member's setup as starting values. Members can customize their categories but the delivery method, label prefix, and max priority settings are org-mandated.

---

## Prerequisites

- Gmail MCP server available in the org's agent environment
- If using Slack delivery: Slack MCP server available
- Org admin has confirmed that members will have access to Gmail OAuth credentials (either per-member or via a shared service account)

---

## Org-Level Parameters

### `delivery_method` [org-mandated]
How triage summaries are delivered to members.
- Options: `slack`, `chat`
- Ask: "How should triage summaries be delivered to your team? Options: 'slack' (sends a DM after each run) or 'chat' (outputs directly in the conversation)."
- If `slack`: validate that a Slack MCP server is connected.

### `label_prefix` [org-mandated]
Prefix for all auto-created Gmail labels. Keeps triage labels namespaced and easy to identify.
- Default: `ai-reviewed-`
- Ask: "What prefix should be used for Gmail labels? Default is 'ai-reviewed-' (creates labels like 'ai-reviewed-spam', 'ai-reviewed-news')."

### `max_priority_emails` [org-mandated]
Maximum number of high-priority emails surfaced per triage run.
- Default: 15
- Ask: "What's the maximum number of high-priority emails to surface per run? Default is 15."

### `default_categories` [org-mandated]
The starter set of classification categories every member gets at setup time. Members can customize their list after setup via `email-triage-config`, but these provide a common baseline.

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

Ask: "These are the default categories every member will start with. Would you like to add any org-specific categories? For example, categories for specific vendor notifications, internal tool alerts, or recurring report types."

For each additional category the admin wants to add, collect: name, description, sender patterns (optional), subject patterns (optional), and action.

---

## Setup Completion

Collection setup is complete when:

1. `collection-setup-responses.md` is written to the collection's `/setup/` directory on the remote filesystem with all org-level parameters in YAML format
2. All parameter values are valid (delivery_method is `slack` or `chat`, label_prefix is a non-empty string, max_priority_emails is a positive integer, default_categories contains at least one category)
3. Admin has confirmed the configuration

The responses file uses this format:

```yaml
## Email Triage Collection Configuration

delivery_method: slack
label_prefix: "ai-reviewed-"
max_priority_emails: 15

default_categories:
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
- `delivery_method`
- `label_prefix`
- `max_priority_emails`
- `default_categories`

### Reset on Upgrade
N/A.

### Requires Admin Attention
- If new org-mandated parameters are added in a future version, the admin will be prompted to configure them.
- If the category schema changes, existing categories will be migrated where possible and the admin notified of any manual adjustments needed.

### Migration Notes
- v1.0 → future versions: migration notes will be added here as new versions are published.
