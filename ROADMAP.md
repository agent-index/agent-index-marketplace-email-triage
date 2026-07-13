# Email Triage — Roadmap

Current version: 1.2.0
Last updated: 2026-04-05

---

## Current State

v1.2 provides automated Gmail inbox triage with configurable categories, priority detection, label-and-archive automation, iterative training, HTML email digests, and a guided tutorial for member onboarding. The v1.1 release moved OAuth app credentials to org-admin ownership so members no longer create Google Cloud projects — they just authorize their Gmail account with a one-time browser flow.

### Known Limitations

- **Gmail only.** The collection is tightly coupled to Gmail's API (labels, archive behavior, search syntax). Outlook/Exchange support would require significant rework of the labeling and archiving scripts.
- **No attachment analysis.** Classification is based on sender, subject, and body text. Attachments (PDFs, images, spreadsheets) are not opened or analyzed. An email with a critical document attached but a generic subject line may be misclassified.
- **Training corrections are sender-heavy.** The correction model learns sender rules effectively but is weaker at content-pattern rules. A member who wants "flag all emails mentioning Project X as high priority" must rely on agent judgment rather than a trainable rule.
- **Digest is label-based, not category-based.** The `email-digest` task reads from a Gmail label, not directly from triage categories. This means the member must configure triage to label emails they want in the digest, which is an extra setup step.
- **No cross-run deduplication for digests.** If the same email is labeled across two triage runs (e.g., label added then re-labeled), the digest may include it twice.

### Known Bugs

None currently tracked.

---

## Wishlist

### v1.3 — Quality of Life

- **Content-pattern training.** Extend the correction model to learn from subject/body patterns, not just sender rules. "Emails about budget reviews should be categorized as finance" would become a trainable rule.
- **Digest deduplication.** Track which message IDs have been included in previous digests to avoid repeats.
- **Category-aware digest.** Allow `email-digest` to pull from triage categories directly rather than requiring a separate label configuration.

### v1.4 — Cross-Collection Integration

- **Capture collection integration.** When triage surfaces a read-later-worthy email (e.g., a newsletter article), offer to capture it directly into the Capture collection.
- **Projects collection integration.** When triage surfaces an email related to a known project (matching project name, members, or keywords), tag the summary with the project reference.

### v2.0 — Structural Changes (breaking)

- **Multi-account support.** Triage across multiple Gmail accounts in a single run. Requires changes to the credential model and per-account category configuration.
- **Outlook/Exchange support.** Abstract the email provider behind a capability interface so different providers can be swapped in. This is a large effort and would likely use the capability provider model.

---

## Design Notes

- The collection deliberately does not mark emails as read or delete them. Triage labels and archives — the member's inbox state is preserved for anything they want to handle manually. This is a safety rail, not a limitation.

- The training loop (triage → train → improved triage) is designed to converge over time. Early runs will have more misclassifications, which is expected. The promotion threshold (3 consistent corrections → hard rule) balances learning speed with noise tolerance.

- The OAuth credential split (org-admin provides `credentials.json`, members authorize individually) was introduced in v1.1 to eliminate the most common setup failure: members being asked to create Google Cloud projects, which most have no idea how to do. This pattern is documented in the authoring guide as a reusable model for any OAuth-based collection.
