---
name: email-triage-train
type: skill
version: 1.2.0
collection: email-triage
description: Review classification decisions from recent triage runs and record corrections that improve future accuracy.
stateful: true
always_on_eligible: false
dependencies:
  skills: []
  tasks:
    - email-triage
external_dependencies: []
---

## About This Skill

Email Triage Train is the iterative learning loop for the email-triage system. After a triage run, members invoke this skill to review the classifications the agent made, correct any mistakes, and build a persistent history of corrections that future triage runs read to improve accuracy.

The skill reads `triage-run-log.json` (written by the `email-triage` task after each run) and writes to `triage-corrections.json` (read by the `email-triage` task at the start of each run). Over time, repeated corrections for the same sender get promoted to high-confidence `sender_rules` that act as automatic quick-matches in future runs.

---

## Directives

### Invocation

When the member invokes this skill:

1. **Check for run log.** Read `triage-run-log.json` from the member's `email-triage` task directory. If no log exists, inform the member: "No triage run log found. Run `email-triage` first, then come back to review the results."

2. **Load existing corrections.** Read `triage-corrections.json` if it exists. This provides context on what's already been learned.

3. **Summarize the run.** Show a brief overview:
   - Run date
   - Total emails processed
   - Breakdown by category
   - Number classified as "other"
   - Number flagged as high priority

4. **Ask the member how they want to review.** Offer two modes:
   - **By category** (recommended) — walk through each category as a group, confirming or correcting in bulk
   - **By individual email** — walk through every decision one by one (thorough but slower)

### Review Flow: By Category

For each category that had emails classified into it during the run:

1. Show the category name and count: "I classified {N} emails as **{category}**."
2. List the emails in that category: sender, subject line, and a one-line reasoning snippet for each.
3. Ask: "Are all of these correct, or are there any that don't belong?"
4. If the member identifies incorrect classifications:
   - For each incorrect email, ask: "What should this have been classified as?" Present the available categories plus "other" and "high-priority other."
   - Record the correction.
5. If all correct, move to the next category.

After reviewing categories, review the "other" emails:

1. Show all emails classified as "other" with their priority flag status.
2. Ask: "Are there any here that should have been categorized instead of left as 'other'?"
3. For any re-categorizations, record the correction with the correct category.
4. Ask: "For the priority flags — did I get the priority right? Any that should have been flagged that weren't, or vice versa?"
5. Record any priority corrections.

### Review Flow: By Individual Email

Walk through each decision in the run log sequentially:

1. Show: sender, subject, snippet, assigned category, priority flag (if "other"), and reasoning.
2. Ask: "Correct?" with options:
   - **Yes** — move on
   - **Wrong category** — ask for the correct one
   - **Should be priority** / **Should not be priority** — record the priority override
3. After every 10 emails, offer to stop: "Want to keep reviewing, or is this enough for now?"

### Recording Corrections

Each correction is appended to the `corrections` array in `triage-corrections.json`:

```json
{
  "date": "{DATE}",
  "message_id": "18f3c2a1b9e",
  "sender": "notifications@github.com",
  "sender_email": "notifications@github.com",
  "subject_snippet": "New pull request in repo-name",
  "agent_classified_as": "notices",
  "correct_category": "dev-notifications",
  "correct_priority": false,
  "member_note": null
}
```

For priority corrections on "other" emails:

```json
{
  "date": "{DATE}",
  "message_id": "19a4d3b2c8f",
  "sender": "cfo@example.com",
  "sender_email": "cfo@example.com",
  "subject_snippet": "Q1 budget review meeting",
  "agent_classified_as": "other",
  "correct_category": "other",
  "correct_priority": true,
  "member_note": "Anything from CFO about budget is always priority"
}
```

The `member_note` field is optional. If the member volunteers reasoning ("anything from this person is important"), capture it — it becomes valuable context for the agent on future runs.

### Promoting Sender Rules

After recording corrections, check whether any sender now has 3 or more corrections pointing to the same category. If so, promote it to a `sender_rule`:

```json
{
  "pattern": "notifications@github.com",
  "correct_category": "dev-notifications",
  "confidence": "high",
  "learned_from": 3,
  "last_updated": "{DATE}"
}
```

Inform the member: "I've noticed you've corrected emails from {sender} to **{category}** {N} times now. I've added a sender rule so future emails from them will be automatically classified as **{category}**."

Also check for priority patterns. If the same sender has been flagged/unflagged 3+ times consistently, add a priority sender rule:

```json
{
  "pattern": "cfo@example.com",
  "priority_override": true,
  "confidence": "high",
  "learned_from": 3,
  "last_updated": "{DATE}"
}
```

### Suggesting Configuration Changes

At the end of a training session, if the skill has identified patterns that would be better served as permanent configuration rather than learned rules, suggest them:

- "I see you keep re-categorizing GitHub notification emails. Want me to add a `dev-notifications` category to your config via `email-triage-config`?"
- "You've marked 5 emails from your CFO as high priority. Want me to add them to your VIP senders list?"

These are suggestions only — the member must confirm before any config changes are made. If they confirm, update `setup-responses.md` directly (the same file `email-triage-config` manages).

### The Corrections File

The full `triage-corrections.json` schema:

```json
{
  "version": "1.0.0",
  "last_trained": "{ISO_TIMESTAMP}",
  "stats": {
    "total_corrections": 0,
    "total_confirmations": 0,
    "sessions_completed": 0
  },
  "sender_rules": [],
  "priority_rules": [],
  "corrections": []
}
```

- `sender_rules` — promoted sender-to-category mappings (read by email-triage Step 4b)
- `priority_rules` — promoted sender priority overrides (read by email-triage Step 6)
- `corrections` — raw correction history (read by email-triage Step 4d as reference examples)
- `stats` — aggregate counts for the member's training activity

### Session Wrap-Up

At the end of a training session:

1. Summarize what was reviewed and corrected: "{N} corrections recorded, {M} sender rules promoted."
2. Update `stats` in the corrections file.
3. If any configuration suggestions were accepted, confirm the changes.
4. Remind the member: "These corrections will take effect on your next triage run."

### Guardrails

- Never modify `triage-run-log.json` — it is read-only input from the triage task.
- Never delete or truncate `corrections` history — only append. Old corrections remain as context.
- Never auto-apply configuration changes without member confirmation.
- If `triage-run-log.json` is stale (more than 7 days old), warn the member and suggest running a fresh triage first.
- Limit `corrections` array to the most recent 500 entries. If exceeded, archive older corrections to `triage-corrections-archive.json` and note the archive date in the main file.
