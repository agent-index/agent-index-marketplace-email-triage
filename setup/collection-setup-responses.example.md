## Email Triage Collection Configuration

delivery_method: slack
label_prefix: "ai-reviewed-"
max_priority_emails: 15

default_categories:
  - name: spam
    label: ai-reviewed-spam
    action: label-and-archive
    signals:
      sender_patterns: []
      subject_patterns: []
      description: >
        Unsolicited, promotional, or junk email. Marketing blasts, sales offers,
        bulk-send messages, no-reply senders with no meaningful content.

  - name: news
    label: ai-reviewed-news
    action: label-and-archive
    signals:
      sender_patterns: []
      subject_patterns: []
      description: >
        Industry newsletters, articles, blog posts, research papers, or curated
        reading lists. Content to be read for professional awareness, not
        notifications about accounts or services.

  - name: notices
    label: ai-reviewed-notices
    action: label-and-archive
    signals:
      sender_patterns: []
      subject_patterns: []
      description: >
        Operational notifications from services and platforms. Terms of service
        updates, billing notices, security alerts, service status updates,
        automated platform notifications.
