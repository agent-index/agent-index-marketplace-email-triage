---
name: email-digest-setup
type: setup
version: 1.2.0
collection: email-triage
description: Setup for the email-digest task — configures source label, relevance criteria, and artifact storage for HTML briefings.
target: email-digest
target_type: task
upgrade_compatible: true
---

## Setup Overview

This setup configures the email digest task, which reads labeled emails from a triage category and produces HTML briefings. The most common use case is summarizing news/newsletter emails, but it works with any triage category.

---

## Pre-Setup Checks

- `email-triage` task is installed in the member's workspace → if not: "Install the email-triage task first — this task reads emails labeled by it."
- Gmail MCP server is connected
- Gmail OAuth credentials are configured (inherited from email-triage setup)

---

## Parameters

### `source_label` [member-overridable]
Gmail label to pull emails from for digest generation.
- Default: the label associated with the member's `news` category (e.g., `ai-reviewed-news`)
- Ask: "Which labeled category would you like to generate digests from? Most people use their 'news' category."

### `processed_label` [member-overridable]
Gmail label applied to emails after they've been included in a digest.
- Default: `email-digest-processed`

### `max_emails_per_run` [member-defined]
Maximum emails to process in a single digest run.
- Default: 10
- Ask: "How many emails should I process per digest run? (Default: 10)"

### `artifact_directory` [member-defined]
Local path where HTML briefing files are saved.
- Default: `{member_workspace}/tasks/email-digest/artifacts/`

### `relevance_criteria` [member-defined]
YAML block describing what content is relevant to this member. Used to decide Featured vs. Skipped sections. Organized by topic area with "what counts" descriptions.
- Ask: "What topics are relevant to your work? I'll use these to decide which articles to feature vs. skip. For example: 'AI & LLMs — foundation models, GenAI releases, AI regulation' or 'Marketing — campaign strategy, brand positioning, competitor launches'."
- Format the response into a structured YAML block.

### `token_dir` [member-defined]
Path to directory containing the member's personal `token.json` (and local copy of org-provided `credentials.json`). Inherited from email-triage setup if already configured.

---

## Setup Completion

1. Write `setup-responses.md` to the member's task directory with all configured parameters
2. Write `manifest.json`
3. Create `artifact_directory` if it doesn't exist
4. Register entry in `member-index.json` with alias `@ai:email-digest`
5. Confirm to member: "Email Digest is set up. Say '@ai:email-digest' to generate a briefing from your labeled emails."

---

## Upgrade Behavior

### Preserved Responses
- `source_label`
- `processed_label`
- `max_emails_per_run`
- `artifact_directory`
- `relevance_criteria`
- `learned_preferences` (accumulated feedback, appended by the task over time)

### Reset on Upgrade
N/A.

### Requires Member Attention
- If the HTML template format changes significantly, members may want to review an example output.

### Migration Notes
- v1.0 → future versions: migration notes will be added here as new versions are published.
