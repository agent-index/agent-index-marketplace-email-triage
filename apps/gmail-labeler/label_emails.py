#!/usr/bin/env python3
"""
Gmail Label Applicator
-----------------------
Applies a Gmail label to one or more messages by message ID.
The label is created automatically if it does not already exist.

This script does no classification or filtering — it just applies the label
you specify to the message IDs you provide. The caller (e.g. an AI agent) is
responsible for deciding which emails get which label.

Part of the email-triage collection. Credentials path is configurable via
--credentials-dir to support per-member credential storage.

Usage:
    # Label a single message
    python label_emails.py --label "ai-reviewed-spam" --message-id 18f3c2a1b9e

    # Label multiple messages at once
    python label_emails.py --label "ai-reviewed-news" \
        --message-id 18f3c2a1b9e --message-id 19a4d3b2c8f

    # Use custom credentials directory
    python label_emails.py --label "ai-reviewed-spam" \
        --credentials-dir /path/to/creds --message-id 18f3c2a1b9e

    # Preview without making changes
    python label_emails.py --label "ai-reviewed-spam" --message-id 18f3c2a1b9e --dry-run

Exit codes:
    0  Success (all labels applied, or dry-run completed)
    1  Error (missing credentials, API failure, etc.)
"""

import sys
import argparse
from pathlib import Path

# --- Dependency check ---
try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError:
    print("ERROR: Missing dependencies. Run:")
    print("  pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client")
    sys.exit(1)

# --- Config ---
SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]


# ─────────────────────────────────────────────
# Auth
# ─────────────────────────────────────────────

def get_gmail_service(credentials_file: Path, token_dir: Path):
    """Authenticate and return a Gmail API service object.

    Args:
        credentials_file: Path to the OAuth credentials.json (org-provided app identity).
        token_dir: Directory where the member's personal token.json is stored/written.
    """
    token_file = token_dir / "token.json"
    creds = None

    if token_file.exists():
        creds = Credentials.from_authorized_user_file(str(token_file), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not credentials_file.exists():
                print(f"ERROR: credentials.json not found at: {credentials_file}")
                print("Your org admin provides this file at collection install time.")
                print("Contact your admin or re-run collection setup.")
                sys.exit(1)
            flow = InstalledAppFlow.from_client_secrets_file(str(credentials_file), SCOPES)
            creds = flow.run_local_server(port=0)
        token_dir.mkdir(parents=True, exist_ok=True)
        with open(token_file, "w") as f:
            f.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)


# ─────────────────────────────────────────────
# Label helpers
# ─────────────────────────────────────────────

def get_or_create_label(service, label_name: str) -> str:
    """Return the label ID for label_name, creating it if it doesn't exist."""
    response = service.users().labels().list(userId="me").execute()
    for lbl in response.get("labels", []):
        if lbl["name"].lower() == label_name.lower():
            return lbl["id"]

    # Not found — create it
    new_label = service.users().labels().create(
        userId="me",
        body={
            "name": label_name,
            "labelListVisibility": "labelShow",
            "messageListVisibility": "show",
        }
    ).execute()
    print(f"Created new Gmail label: '{label_name}' (id: {new_label['id']})")
    return new_label["id"]


# ─────────────────────────────────────────────
# Core
# ─────────────────────────────────────────────

def apply_label_to_messages(service, message_ids: list, label_id: str, label_name: str, dry_run: bool) -> bool:
    """Add label_id to each message in message_ids. Returns True if all succeeded."""
    success = 0
    errors = 0

    for msg_id in message_ids:
        prefix = "[DRY RUN] " if dry_run else ""
        try:
            if not dry_run:
                service.users().messages().modify(
                    userId="me",
                    id=msg_id,
                    body={"addLabelIds": [label_id]}
                ).execute()
            print(f"{prefix}Labeled {msg_id} -> '{label_name}'")
            success += 1
        except HttpError as e:
            print(f"ERROR: Could not label message {msg_id}: {e}")
            errors += 1

    print(f"\nDone. {success} labeled, {errors} failed.")
    return errors == 0


# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Apply a Gmail label to one or more messages by ID."
    )
    parser.add_argument(
        "--label", required=True,
        help='Gmail label to apply (e.g. "ai-reviewed-spam"). Created automatically if it does not exist.'
    )
    parser.add_argument(
        "--message-id", dest="message_ids", action="append", required=True, metavar="ID",
        help="Gmail message ID to label. Repeat this flag for multiple messages."
    )
    parser.add_argument(
        "--credentials-dir", dest="credentials_dir", default=None, metavar="DIR",
        help="(Legacy) Directory containing both credentials.json and token.json. "
             "Prefer --credentials-file and --token-dir for the split model."
    )
    parser.add_argument(
        "--credentials-file", dest="credentials_file", default=None, metavar="FILE",
        help="Path to credentials.json (org-provided OAuth app identity). "
             "Overrides --credentials-dir for the credentials file."
    )
    parser.add_argument(
        "--token-dir", dest="token_dir", default=None, metavar="DIR",
        help="Directory for the member's personal token.json. "
             "Overrides --credentials-dir for the token file."
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print what would happen without making any changes."
    )
    args = parser.parse_args()

    # Resolve credential paths: new split flags take precedence over legacy --credentials-dir
    base_dir = Path(args.credentials_dir) if args.credentials_dir else Path(__file__).parent
    creds_file = Path(args.credentials_file) if args.credentials_file else base_dir / "credentials.json"
    token_dir = Path(args.token_dir) if args.token_dir else base_dir

    if args.dry_run:
        print("(DRY RUN — no changes will be made)\n")

    service = get_gmail_service(creds_file, token_dir)
    label_id = get_or_create_label(service, args.label)
    ok = apply_label_to_messages(service, args.message_ids, label_id, args.label, args.dry_run)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
