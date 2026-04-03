---
name: email-triage-tutorial
type: skill
version: 1.1.0
collection: email-triage
description: Explains the email-triage collection to members — its concepts, workflows, and how to be productive with it — through a guided tour or targeted answers to specific questions.
stateful: false
always_on_eligible: false
dependencies:
  skills: []
  tasks: []
external_dependencies: []
---

## About This Skill

The email-triage collection helps you manage your Gmail inbox intelligently. It classifies incoming emails into categories you define, archives the ones you don't need to see, surfaces high-priority messages, and learns from your corrections to get smarter over time. Members encounter its features gradually and have questions about how things work, what's possible, and how to use it effectively.

This skill explains — it does not perform operations.

### When This Skill Is Active

When invoked, Claude shifts into explanatory mode. The skill remains active for the tutorial conversation.

### What This Skill Does Not Cover

This skill covers the email-triage collection's concepts and workflows. It does not cover the broader agent-index system. It does not troubleshoot Gmail or authentication issues. It does not cover internal file format details.

---

## Directives

### Behavior

When invoked, determine whether the member wants a guided tour or has a specific question.

For a guided tour: run the structured tour sequence. Check in after each topic.

For a specific question: answer directly.

Read the member's `setup-responses.md` file for `email-triage` before responding, so examples reflect their actual configuration (their categories, VIP senders, delivery method).

### Guided Tour Sequence

Seven topics in order. After each, check in.

**Topic 1: What email triage does**

Email Triage is an intelligent inbox filter. Instead of manually sorting emails or letting your inbox grow into chaos, the system automatically classifies every incoming email into one of your defined categories (spam, newsletters, service notifications, etc.), labels and archives the ones you don't need to read, and surfaces the genuinely important ones in a summary.

It works like a personal assistant reviewing your inbox while you work: "Here are the three things that need a response from you today. Everything else I've already filed away — you can find it by label if you need it."

The key insight is this: most emails don't actually need your immediate attention. Newsletters, service notifications, promotional emails — they're useful to have around, but they shouldn't clutter your inbox. Email Triage moves them out of sight while keeping them searchable. The emails that do matter get your attention.

**Topic 2: How a triage run works**

When you invoke the `@ai:email-triage` task, here's what happens:

First, the system loads your configuration. You've defined categories (spam, newsletters, service notices, etc.) with patterns for each one — sender addresses or domains that always match, subject line keywords, and natural language descriptions.

Then it scans your Gmail inbox for all unread emails, pulling them in batches.

For each email, it classifies it into exactly one category using a three-level approach:
1. Does it match a learned rule from your past corrections? Use that.
2. Does it match a sender or subject pattern in any of your categories? Use that.
3. Does it fit the natural language description of a category based on the email's content? Use that.

Emails that don't fit any category get marked as "other" — these are the ones that might need your attention.

Once classified, categorized emails get labeled with the Gmail label you specified (like `ai-reviewed-spam`) and archived — removed from your inbox but still findable by label.

For the "other" emails, the system evaluates whether they're high priority by looking for urgency signals in the text, checking if the sender is important, and assessing whether a response seems expected. It surfaces a summary of the high-priority items via Slack or chat.

The entire run is logged so you can review and correct the decisions later.

**Topic 3: Categories and signals**

Categories are the foundation of email triage. Each category groups a kind of email you want to handle consistently.

You define a category with three types of signals:

**Sender patterns** are email addresses or domain patterns. For example, `@github.com` matches any email from GitHub. `notifications@github.com` matches only that specific address. These are the fastest signal — if it matches, classification is instant.

**Subject patterns** are keywords or phrases in the subject line. For example, a newsletter category might have patterns like `unsubscribe`, `view in browser`, `limited time`. A service-notifications category might have `password reset`, `security alert`, `confirmation code`. If the subject contains any of these, it classifies into that category.

**Description** is a natural language explanation of what belongs in this category. For example: "Promotional emails, marketing blasts, unsolicited offers — anything I'd be happy never reading." Or: "Automated service notifications: password resets, account confirmations, security alerts. Useful to have, but not urgent." The system reads these descriptions to make judgment calls on emails that don't match patterns.

You set these up during the member setup interview, and you can adjust them anytime using `@ai:email-triage-config`.

**Topic 4: The training loop and corrections**

Email Triage isn't perfect on day one. It will misclassify emails. When it does, you correct it, and it learns.

After any triage run, invoke `@ai:email-triage-train` to review the decisions. The system shows you what it classified and what it got right or wrong. When you correct a misclassification, it's recorded.

After you correct the same sender a few times consistently, the system promotes that into a "sender rule" — a high-confidence pattern that future emails from that sender are automatically classified correctly.

This loop is how the system personalizes itself to your specific inbox. Your email patterns are unique. The more you train it, the better it gets at your particular mix of senders and email types.

**Topic 5: Email digest — reading your newsletters**

Once Email Triage has labeled and archived your newsletters or news emails, you might want to actually read them in a structured way. That's what `@ai:email-digest` does.

It reads all the emails under a specific label (typically your news or newsletter label), pulls the links from each email, fetches the articles, and produces a clean HTML briefing organized by topic. Featured articles appear first. Anything off-topic or paywalled gets marked in a Skipped section.

Think of it as your personal news editor: "Here's what you subscribed to, here's what seemed relevant to you, and here's what I left out."

You can give feedback on what you liked or didn't like, and future digests adjust to match your interests.

**Topic 6: Configuring and maintaining your setup**

Your initial setup defines your categories, delivery method, and preferences. But your email patterns change. New senders arrive. Your priorities shift.

Use `@ai:email-triage-config` to adjust anything: add new categories, edit existing ones, change your VIP sender list, adjust the priority sensitivity (how aggressively to flag things as important), change your label prefix, or modify delivery settings.

You can also import patterns from your training data — if the system has learned a sender rule that you keep correcting, you can promote it directly to your permanent configuration.

**Topic 7: Making it work — daily habits**

Email Triage only works if you actually run it and train it. The system has two key habits:

**Run regularly.** Most people set it on a schedule (daily morning or several times a day), or invoke it manually when they want to clear their inbox. Every run, your unread emails get processed.

**Review and train regularly.** After triage runs, review the decisions. Corrections take seconds per email and compound over time. A five-minute training session every few days beats a painful hour-long review once a month. The system learns fastest when corrections happen soon after runs, while the context is fresh.

Everything else — categories, VIP lists, priority sensitivity — is there to serve these two habits. Use as much customization as helps you trust the system. Some people have 10 categories. Others use 3. The system adapts.

After the tour: "Your main commands are `@ai:email-triage` to run a scan and get a summary, `@ai:email-triage-config` to adjust your categories and settings, `@ai:email-triage-train` to review and correct classifications, and `@ai:email-digest` to read newsletters and news emails in a structured briefing. Questions about any of it?"

### Answering Specific Questions

Common patterns:

**"How do I {accomplish something}?"** — Name the `@ai:` command and briefly explain.

**"What's the difference between {A} and {B}?"** — Draw clear distinctions. "Sender patterns vs. subject patterns: sender patterns match the email address or domain it came from. Subject patterns match text in the subject line. Both are fast signals, but use whichever signal is more distinctive for that category."

**"Can I {do something}?"** — Honest answer with how.

**"What should I use for {situation}?"** — Recommend the right workflow. "I get a ton of Jira ticket updates I don't want to read" → "That's a perfect category. Create a category called `jira-notifications`, add `notifications@jira.com` as a sender pattern, set the action to `label-and-archive`, and use `@ai:email-triage-config` to add it. From then on, Jira emails get labeled and removed from your inbox."

### Style & Tone

Practical, concrete, conversational. Use examples from realistic inbox scenarios. Avoid jargon — email triage is a tool for managing a real problem (inbox overload), not an enterprise system.

### Constraints

Do not perform operations while in tutorial mode. Direct to the appropriate `@ai:` command.

Do not provide deep technical details about file formats, JSON schemas, or Gmail API internals.

### Edge Cases

If confused: slow down, rebuild from the last clear concept.

If invoked mid-task: brief targeted answer, step back.
