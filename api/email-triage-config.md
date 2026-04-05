---
name: email-triage-config
type: skill
version: 1.0.0
collection: email-triage
description: Interactively manage email triage categories, VIP senders, ignore lists, and classification parameters.
stateful: true
always_on_eligible: false
dependencies:
  skills: []
  tasks: []
external_dependencies: []
---

## About This Skill

Email Triage Config is the interactive management interface for all email-triage classification settings. Members invoke this skill to add, edit, or remove triage categories, manage their VIP sender and ignore lists, adjust priority sensitivity, and preview how changes would affect classification.

This skill reads and writes to the member's `setup-responses.md` file for the `email-triage` task. Changes take effect on the next triage run.

---

## Directives

### Invocation

When the member invokes this skill, begin by reading their current `setup-responses.md` for `email-triage`. Display a summary of their current configuration:
- Number of configured categories with names
- Number of VIP senders
- Number of ignored senders
- Current priority sensitivity setting
- Current delivery method
- Current label prefix
- Current max priority emails

Then ask what they'd like to do.

### Supported Operations

**Add a category**
Walk the member through defining a new category:
1. Ask for a name (kebab-case, e.g., `jira-notifications`)
2. Ask for a description — what kinds of emails belong here? This becomes `signals.description`.
3. Ask for sender patterns — specific email addresses or domains that always match (optional)
4. Ask for subject patterns — subject line keywords or phrases that always match (optional)
5. Ask what action to take: `label-and-archive` (remove from inbox), `label-only` (label but keep in inbox), or `skip` (classify but take no action)
6. Generate the Gmail label name using the member's `label_prefix` + category name (e.g., `ai-reviewed-jira-notifications`)
7. Confirm the full category definition with the member before saving

**Edit a category**
Show the member their existing categories and let them select one to modify. They can change any field: description, sender patterns, subject patterns, or action. Confirm changes before saving.

**Remove a category**
Show the member their existing categories and let them select one to remove. Warn that this does not delete the Gmail label or re-classify already-labeled emails. Confirm before removing.

**Manage VIP senders**
Show the current VIP list. The member can add or remove email addresses or domains. VIP senders always flag as high-priority in triage runs.

**Manage ignore list**
Show the current ignore list. The member can add or remove email addresses or domains. Ignored senders are always classified into the first `label-and-archive` category (typically spam).

**Adjust priority sensitivity**
Explain the three levels:
- `high` — flag if any one priority criterion is met (most emails flagged)
- `medium` — flag if two or more criteria are met (balanced)
- `low` — flag only if all three criteria are met (fewest emails flagged)
Let the member choose. Default is `high`.

**Change delivery method**
Let the member switch between `slack` and `chat`. If switching to `slack`, ensure they have a `slack_user_id` configured (prompt for it if not). If switching away from `slack`, note that their `slack_user_id` will be preserved in case they switch back.

**Change label prefix**
Let the member change the prefix applied to all Gmail labels. Warn that changing the prefix does not rename existing Gmail labels — only new labels created going forward will use the new prefix. Existing categories will have their `label` field updated to use the new prefix.

**Change max priority emails**
Let the member adjust the maximum number of high-priority emails surfaced per run.

**Import from training data**
If `triage-corrections.json` exists, offer to review learned `sender_rules` and promote them to permanent category `sender_patterns`. This closes the loop between training and configuration: corrections that have been made enough times become explicit rules.

### Writing Changes

After any modification, update the member's `setup-responses.md` with the new configuration. The configuration section uses this format:

```yaml
## Email Triage Configuration

delivery_method: slack
label_prefix: "ai-reviewed-"

categories:
  - name: spam
    label: ai-reviewed-spam
    action: label-and-archive
    signals:
      sender_patterns:
        - "@marketing.example.org"
      subject_patterns:
        - "unsubscribe"
        - "limited time offer"
      description: >
        Unsolicited, promotional, or junk email. Marketing blasts,
        sales offers, bulk-send messages the member would not want to read.

  - name: news
    label: ai-reviewed-news
    action: label-and-archive
    signals:
      sender_patterns: []
      subject_patterns: []
      description: >
        Industry newsletters, articles, blog posts, research papers,
        or curated reading lists. Content to be read for professional
        awareness, not notifications about accounts or services.

vip_senders: []
ignore_senders: []
priority_sensitivity: high
max_priority_emails: 15
```

### Validation

Before saving any change:
- Category names must be unique and kebab-case
- Label names must be unique across all categories
- Sender patterns must be valid email addresses or domains (contain `@` or start with `@`)
- A category must have at least a description (patterns are optional)

### Guardrails

- Never modify `token_dir` — that is set during setup and tied to the member's OAuth tokens
- Never delete the member's `triage-corrections.json` or `triage-run-log.json`
- Always confirm destructive operations (remove category, clear VIP list) before executing
