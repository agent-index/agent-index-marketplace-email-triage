# Changelog

## [1.2.1] — 2026-04-19

### Added
- **Natural language trigger phrases in `collection.json`.** API entries now include trigger arrays that map conversational phrases to capabilities, powering the routing layer introduced in agent-index-core 3.0.5. Members can say things like "triage my email" or "what's important in my email" instead of using `@ai:` alias syntax. Triggers are customizable per-member via `routing.json`.

## [1.2.0] — 2026-04-02

### Added
- **email-triage-tutorial skill** — Guided tutorial explaining the email-triage collection to members through interactive learning and targeted answers to specific questions about concepts, workflows, and productivity best practices.

## [1.1.0] — 2026-04-01

### Changed
- **OAuth credentials are now org-admin provided.** The `credentials.json` (Google Cloud OAuth app identity) is configured by the org admin at collection install time and stored on the remote filesystem. Members no longer need to create Google Cloud projects or download credentials — they only authorize their own Gmail account via a one-time browser flow.
- Renamed `credentials_path` parameter to `token_dir` to reflect that it holds the member's personal `token.json`, not the org-level app credentials.
- Updated `label_emails.py` and `archive_emails.py` to accept `--credentials-file` and `--token-dir` as separate flags. Legacy `--credentials-dir` still works for backwards compatibility.
- Updated `collection-setup.md` with new `gmail_credentials_json` [org-mandated] parameter and credential setup flow.
- Simplified `email-triage-setup.md` prerequisites — members now just run a browser auth flow instead of setting up a Google Cloud project.

## [1.0.0] — 2026-03-26

### Added
- Initial release of the email-triage collection
- `email-triage` task — batch inbox scan, configurable classification, label-and-archive, priority summary delivery
- `email-triage-config` skill — interactive category and sender rule management
- `email-triage-train` skill — post-run classification review and iterative correction learning
- `email-digest` task — HTML briefing generation from labeled email categories
- Bundled `gmail-labeler` and `gmail-archiver` Python scripts with configurable credential paths
- Three-tier configuration: org-mandated, role-suggested, and member-defined parameters
- Built-in default categories: spam, news, notices
