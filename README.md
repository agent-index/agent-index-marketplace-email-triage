# Email Triage

Automated Gmail inbox triage for teams and individuals. Classifies unread emails into configurable categories, labels and archives non-essential messages, identifies high-priority emails, and delivers a structured summary via Slack DM or chat.

## What It Does

Email Triage scans your Gmail inbox on each run, classifies every unread email, and takes action based on your configuration. Emails matching your defined categories (spam, newsletters, service notices, etc.) get labeled and archived automatically. Everything else is evaluated for urgency and surfaced in a priority summary. Over time, a built-in training loop lets you correct misclassifications so the system gets smarter with every run.

## Included Skills and Tasks

- **email-triage** (task) — The core inbox scan. Retrieves unread emails in batches, classifies each into a configured category or "other," labels and archives categorized emails, evaluates priority for remaining emails, and delivers a summary.
- **email-triage-config** (skill) — Interactive category management. Add, edit, or remove triage categories. Manage VIP senders and ignore lists. Preview how configuration changes would affect classification.
- **email-triage-train** (skill) — Review and correct classification decisions from recent runs. Corrections accumulate into sender rules and example-based guidance that the triage task reads on future runs to improve accuracy.
- **email-digest** (task) — Reads emails under a specified label (e.g., `ai-reviewed-news`) and produces an HTML briefing with article summaries.

## Prerequisites

- A Gmail account with OAuth2 credentials configured for the `gmail.modify` scope (setup guide provided during install)
- A Gmail MCP server connected to the agent's session
- A Slack MCP server connected to the agent's session (optional — only needed if delivery method is Slack)

## Workflow

1. **Install** — Admin installs the collection and configures org-level defaults (delivery method, label prefix, default categories).
2. **Member setup** — Each member configures their Slack ID, Gmail credentials, and personalizes their category list.
3. **Run** — Member invokes `email-triage` (manually or on a schedule). Inbox is scanned, categorized, and summarized.
4. **Train** — Member invokes `email-triage-train` to review recent classifications and correct mistakes. Corrections feed back into future runs.
5. **Tune** — Member uses `email-triage-config` to add new categories or adjust rules as their email patterns change.

## Version History

See [CHANGELOG.md](CHANGELOG.md).
