---
name: email-digest
type: task
version: 1.0.0
collection: email-triage
description: Read emails under a specified triage label, fetch linked articles, and produce a structured HTML briefing with featured and skipped sections.
stateful: true
produces_artifacts: true
produces_shared_artifacts: false
dependencies:
  skills: []
  tasks:
    - email-triage
external_dependencies:
  - Gmail MCP
  - Gmail API OAuth credentials
reads_from: null
writes_to: null
---

## About This Task

Email Digest reads emails that were classified and labeled by the `email-triage` task, fetches their linked articles, and produces a self-contained HTML briefing. It's designed primarily for newsletter/news digests but works with any triage category.

The task marks processed emails with a secondary label so they're not re-processed on future runs. The HTML briefing is saved locally and presented to the member.

---

## Configuration

This task reads its configuration from the member's `setup-responses.md` file.

### Required Parameters

- **`source_label`** — Gmail label to pull emails from (default: the label associated with the `news` category, e.g., `ai-reviewed-news`)
- **`processed_label`** — Gmail label to apply after processing (default: `email-digest-processed`)
- **`token_dir`** — path to directory containing the member's personal `token.json` and local copy of `credentials.json` (inherited from email-triage setup)
- **`max_emails_per_run`** — maximum emails to process per run (default: 10)
- **`artifact_directory`** — local path to save HTML briefings

### Optional Parameters

- **`relevance_criteria`** — YAML block describing what content is relevant to this member, organized by topic area. Used to decide Featured vs. Skipped.
- **`learned_preferences`** — accumulated feedback from prior runs (appended by this task after member feedback)

---

## Workflow

### Step 1 — Find Emails to Process

Search Gmail for emails with `source_label` AND NOT `processed_label`. Sort newest-first. Process up to `max_emails_per_run` emails. Note in the briefing header how many total remain unprocessed.

### Step 2 — Read and Evaluate Each Email

For each email:
1. Read the full subject line and body text.
2. Extract all substantive links. Skip: footer links, unsubscribe links, social media profile links, ad tracker URLs (utm_* parameters, click-tracking domains).
3. Use web fetch to read each substantive linked article in full.
4. If an article is paywalled, blocked, or inaccessible, note it explicitly — do not skip silently.
5. Determine relevance using `relevance_criteria` and `learned_preferences`. Learned preferences take priority over default criteria.

### Step 3 — Label Processed Emails

Apply the `processed_label` to all processed message IDs using the labeling script:

```bash
python {apps_path}/gmail-labeler/label_emails.py \
    --label "{processed_label}" \
    --credentials-file "{token_dir}/credentials.json" \
    --token-dir "{token_dir}" \
    --message-id <ID> [--message-id <ID> ...]
```

### Step 4 — Build the HTML Briefing

Create a self-contained HTML file (inline CSS only, no external dependencies):

**Header block:**
- Title: "Email Digest — {DATE}"
- Stats: X emails processed, Y articles read, Z featured, W skipped

**Section 1 — Featured:**
Organized by topic subheadings (derived from `relevance_criteria` areas or auto-grouped by theme). Each item:
- Headline (linked to source)
- Source name
- Summary: detailed enough to replace reading the original — preserve key insights, data points, named entities, and strategic implications. Use prose unless the source is a list/report format.

**Section 2 — Skipped:**
For each item: 1–2 sentences describing what it was about, plus a tag: [off-topic], [promotional], [generic], [paywalled], or [duplicate].

**Styling:**
- Clean, readable layout — 16px body font, comfortable line height
- Clear visual separation between Featured and Skipped
- Featured items should feel like a well-edited briefing document
- Skipped section can be more compact and visually muted
- Fully self-contained

### Step 5 — Save the HTML Artifact

Determine filename: `digest-YYYY-MM-DD.html`. If it exists, append `-2`, `-3`, etc. until an unused name is found. Save to `artifact_directory`.

Present the file to the member using available file presentation tools.

### Step 6 — Summarize and Invite Feedback

After presenting the file, give a 2–3 sentence summary of key themes in the Featured section. Then ask:

> "Does anything in the Featured section not feel relevant? Or did anything in Skipped that you'd have wanted to see? Let me know and I'll update the criteria so future digests are better calibrated."

### Step 7 — Update Learned Preferences (Only If Feedback Given)

If the member provides feedback, append to the `learned_preferences` section of `setup-responses.md`:

```
- [YYYY-MM-DD] Exclude: {what to exclude and why}
- [YYYY-MM-DD] Include: {what to prioritize and why}
```

---

## Directives

- Process only emails with the specified `source_label`. Never read the full inbox.
- Do not mark any email as read.
- Do not delete or reply to any email.
- Always label processed emails to prevent re-processing.
- If web fetch fails for a linked article, note it in the briefing as [inaccessible] rather than silently skipping.
- Learned preferences always override default relevance criteria.
- Save the HTML artifact before presenting — do not present unsaved content.
