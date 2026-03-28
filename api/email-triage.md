---
name: email-triage
type: task
version: 1.0.0
collection: email-triage
description: Scan Gmail inbox for unread emails, classify into configured categories, label and archive non-essential emails, evaluate priority for the rest, and deliver a structured summary.
stateful: true
produces_artifacts: false
produces_shared_artifacts: false
dependencies:
  skills: []
  tasks: []
external_dependencies:
  - Gmail MCP
  - Gmail API OAuth credentials
  - Slack MCP
reads_from: null
writes_to: null
---

## About This Task

Email Triage is the core inbox processing task. It scans a member's Gmail inbox in batches, classifies each unread email into one of the member's configured categories or "other," labels and archives categorized emails, evaluates priority for remaining emails, and delivers a formatted summary via Slack DM or chat.

Classification is driven by three inputs, checked in order of precedence:
1. **Sender rules** — learned corrections from `email-triage-train` (highest confidence)
2. **Category signals** — sender patterns, subject patterns, and natural-language descriptions from the member's config
3. **Agent judgment** — contextual reasoning for emails that don't match any pattern

---

## Configuration

This task reads its configuration from the member's `setup-responses.md` file at runtime. All parameters below are set during setup or via the `email-triage-config` skill.

### Required Parameters

- **`categories`** — Array of classification categories. Each category has:
  - `name` (string) — kebab-case identifier
  - `label` (string) — Gmail label to apply (e.g., `ai-reviewed-spam`)
  - `action` (string) — one of `label-and-archive`, `label-only`, `skip`
  - `signals.sender_patterns` (array) — email addresses or domains that match this category
  - `signals.subject_patterns` (array) — subject line substrings or patterns
  - `signals.description` (string) — natural language description of what belongs in this category, used for agent judgment when patterns don't match

- **`delivery_method`** — `slack` or `chat`
- **`slack_user_id`** — Slack user ID for DM delivery (required if delivery_method is `slack`)
- **`credentials_path`** — path to directory containing Gmail OAuth `credentials.json` and `token.json`
- **`label_prefix`** — string prefix for all auto-created labels (default: `ai-reviewed-`)
- **`max_priority_emails`** — maximum high-priority emails to surface per run (default: 15)

### Optional Parameters

- **`vip_senders`** — email addresses or domains that always flag as high-priority
- **`ignore_senders`** — email addresses or domains that always classify as spam
- **`priority_sensitivity`** — `high`, `medium`, or `low` (controls how many priority criteria must be met)

---

## Workflow

### Step 1 — Load Configuration

Read the member's `setup-responses.md` to load all parameters: categories, delivery method, credentials path, VIP senders, ignore list, and priority sensitivity.

If `triage-corrections.json` exists in the member's task directory, load it. Extract `sender_rules` for quick-match classification and keep `corrections` in context as reference examples for ambiguous cases.

### Step 2 — Retrieve Inbox Emails (Batch Loop)

Search Gmail inbox for all unread messages (`is:unread in:inbox`). Retrieve metadata for each: sender name, sender email address, subject line, date received, thread ID, message ID, and body snippet.

Retrieve up to 50 emails per batch. Process Steps 3–5 for the current batch, then check for remaining unread emails. Continue looping until no new emails remain to process. Track all processed message IDs across batches to avoid re-processing.

### Step 3 — Filter Out Replied Threads

For each unread email, check whether the member has sent any reply in the same thread. Use the thread ID to inspect whether any message in the thread was sent by the member after the unread email was received. Exclude any email whose thread contains a member-sent reply from further processing.

### Step 4 — Classify Each Email

For each remaining (unreplied, unread) email, classify it into exactly one category using this precedence:

**4a. Check ignore list.** If the sender matches any entry in `ignore_senders`, classify as the first category with action `label-and-archive` (typically spam).

**4b. Check learned sender rules.** Read `sender_rules` from `triage-corrections.json`. If the sender matches a rule with confidence `high`, apply the rule's category without further analysis.

**4c. Check category signals.** For each configured category, check `sender_patterns` and `subject_patterns`. If any pattern matches, classify into that category.

**4d. Check correction examples.** Scan recent `corrections` from `triage-corrections.json`. If the current email closely resembles a previously corrected email (similar sender domain, similar subject pattern), weight classification toward the corrected category.

**4e. Agent judgment.** Read each category's `signals.description` and use contextual reasoning to classify. Consider the email's sender, subject, body snippet, and the natural language descriptions of all categories. If no category fits, classify as `other`.

**When in doubt, classify as `other`.** It is safer to surface an email than to silently label and skip it.

### Step 5 — Label and Archive Categorized Emails

For all emails classified into a category (not `other`), apply the appropriate Gmail label using the labeling script:

```bash
python {apps_path}/gmail-labeler/label_emails.py \
    --label "{label}" \
    --credentials-dir "{credentials_path}" \
    --message-id <ID> [--message-id <ID> ...]
```

Batch all IDs of each category into a single call per label where possible. Labels are created automatically in Gmail if they don't exist.

After labeling, archive all successfully labeled emails whose category action is `label-and-archive`:

```bash
python {apps_path}/gmail-archiver/archive_emails.py \
    --credentials-dir "{credentials_path}" \
    --message-id <ID> [--message-id <ID> ...]
```

If any script call fails for individual messages, note the failure but continue processing.

### Step 6 — Evaluate Priority of "Other" Emails

For each email classified as `other`, assess whether it is high priority. The number of criteria required depends on `priority_sensitivity`:
- `high` sensitivity: one or more criteria → flagged (default)
- `medium` sensitivity: two or more criteria → flagged
- `low` sensitivity: all three criteria → flagged

**A. Urgent Keywords**
The subject line or body contains urgency signals: urgent, ASAP, time-sensitive, deadline, action required, action needed, immediate, by EOD, overdue, follow up, reminder, past due, awaiting your response, blocked, blocker.

**B. Important Sender**
The sender appears in `vip_senders`, or agent judgment infers importance from: title in signature (manager, director, VP, C-level), client/partner organization domain, high-frequency correspondence pattern, or the email is addressed directly to the member (To field, not CC).

Check learned sender rules and corrections for any prior priority overrides for this sender.

**C. Content Judgment**
The content implies a timely response is expected or failure to respond has meaningful consequences: meeting requests with deadlines, approval requests, legal or contractual matters, customer escalations.

**Non-priority signals (down-rank):**
- CC-only emails with no direct action requested
- No-reply addresses classified as other
- BCC-line emails

Limit total high-priority emails to `max_priority_emails` per run. If more qualify, surface the most urgent based on recency and keyword strength.

### Step 7 — Write Run Log

Write a `triage-run-log.json` file to the member's task directory. This log is consumed by `email-triage-train` for the review flow.

```json
{
  "run_date": "{ISO timestamp}",
  "batch_count": 0,
  "totals": {
    "processed": 0,
    "by_category": {},
    "other": 0,
    "high_priority": 0,
    "skipped_replied": 0
  },
  "decisions": [
    {
      "message_id": "",
      "sender": "",
      "sender_email": "",
      "subject": "",
      "received": "",
      "classified_as": "",
      "priority_flagged": false,
      "reasoning": "",
      "classification_source": "sender_rule|signal_match|correction_example|agent_judgment"
    }
  ]
}
```

### Step 8 — Compose and Deliver Summary

Compose the summary with counts across all batches and high-priority email details.

**If delivery_method is `slack`:**
Send a single formatted Slack DM to `slack_user_id` using this format:

```
📬 *Email Triage — {DATE}*

🗂 Processed {TOTAL} unread email(s) across {BATCH_COUNT} batch(es): {CATEGORY_COUNTS}.

{If high-priority emails exist:}
{COUNT} high-priority email(s) need a response:

---

*1. {SUBJECT LINE}*
👤 From: {SENDER NAME} <{SENDER EMAIL}>
📅 Received: {DATE & TIME}
📝 Summary: {1–3 sentence summary}
⚡ Why flagged: {One sentence justification}

---
```

If no high-priority emails:
```
📬 *Email Triage — {DATE}*

🗂 Processed {TOTAL} unread email(s) across {BATCH_COUNT} batch(es): {CATEGORY_COUNTS}.

✅ No high-priority unreplied emails found in your inbox.
```

**If delivery_method is `chat`:**
Output the same formatted summary directly in the conversation.

Wait until all batches are complete before delivering. Do not send intermediate summaries.

---

## Directives

- **Only access the Inbox label.** Do not read Sent, Spam, Drafts, or any other folder/label.
- **Do not mark any email as read.** Leave all read/unread status exactly as found.
- **Do not delete or reply to any email.**
- **Only remove the INBOX label** from emails that have been successfully labeled via the labeling script. Do not archive emails that failed labeling.
- **Only apply labels via the bundled gmail-labeler script.** Do not apply labels through any other mechanism.
- **Only surface "other" emails that are unread AND unreplied** in the priority summary.
- **When in doubt, classify as other.** A false positive (surfacing a non-urgent email) is preferable to a false negative (missing a genuinely urgent one).
- **Always write the run log.** The training skill depends on it. If the log write fails, note the error but do not abort the run.

---

## Error Handling

- If Gmail access fails, deliver an error message: "Email Triage failed: could not access Gmail inbox. Please check permissions."
- If the labeling or archiving script fails for any message, log the error and continue — do not abort the task.
- If Slack delivery fails and delivery_method is `slack`, fall back to outputting the summary in chat.
- If the inbox contains 0 unread emails, deliver the "no high-priority emails" message.
- If `setup-responses.md` is missing or incomplete, halt and instruct the member to run setup.
