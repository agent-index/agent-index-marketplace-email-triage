# Changelog

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
