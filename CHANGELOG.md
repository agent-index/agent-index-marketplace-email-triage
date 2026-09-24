# Changelog

## [1.2.3] — 2026-09-23 — adopt core's `apps_path`

**PATCH — no capability behaviour changes. Requires agent-index-core 3.29.2 or later.**

### Removed

- **`apps_path` declaration** from `email-triage-setup.md`, and its `parameter_provenance` entry from `email-triage-manifest.json`. It was `[member-defined]`, which prompted the member to type a path — for a directory that, before core 3.29.0, did not exist on their machine at all, and that core now computes and supplies as a core-injected parameter (`standards.md`, "Core-Injected Parameters").

  `{apps_path}` is unchanged in `email-triage.md` and `email-digest.md` where the labeling and archiving scripts are invoked. Core supplies the value.

### Unchanged, deliberately

- **`token_dir` and `{member_workspace}/apps/gmail-credentials/` are untouched.** That directory is OAuth credential space, placed by this collection's own setup template, and named for the external *app* it authenticates against. It has nothing to do with `installed/{collection}/apps/`, which holds bundled scripts and is placed — and wholesale-replaced on every upgrade — by core. The two share a word and nothing else. Collapsing them would put member credentials in a directory core deletes on each collection upgrade. Core's authoring guide now calls this distinction out explicitly.

### Known gap (not fixed here)

This collection's `apps/requirements.txt` pins three third-party packages — `google-api-python-client`, `google-auth-oauthlib`, `google-auth-httplib2`. Core materializes `requirements.txt` onto the member's machine but does not create an environment or run `pip`, so the labeling and archiving scripts are present and will still fail on first run unless the member has those packages. `bug-reports` and `cx-studio` are standard-library only, so email-triage is currently the only collection with this problem. Tracked in core's `ROADMAP.md`; a real fix needs either a sanctioned per-collection environment or an explicit install step at setup.

## [1.2.2] — 2026-06-06 — fleet docs hygiene (post-audit sweep)

### Fixed (docs only)

- All capability manifests re-stamped with the correct `collection_version` (preflight Check 2 compliance).

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
