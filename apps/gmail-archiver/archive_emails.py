#!/usr/bin/env python3
"""
Gmail Archiver
---------------
Removes the INBOX label from one or more messages by message ID, effectively
archiving them out of the inbox. Messages remain accessible in All Mail and
under any other labels they carry.

This script does no classification or filtering — it just archives the
message IDs you provide. The caller (e.g. an AI agent) is responsible for
deciding which emails to archive.

Part of the email-triage collection. Credentials path is configurable via
--credentials-dir to support per-member credential storage.

Usage:
    # Archive a single message
    python archive_emails.py --message-id 18f3c2a1b9e

    # Archive multiple messages at once
    python archive_emails.py \
        --message-id 18f3c2a1b9e --message-id 19a4d3b2c8f

    # Use custom credentials directory
    python archive_emails.py \
        --credentials-dir /path/to/creds --message-id 18f3c2a1b9e

    # Preview without making changes
    python archive_emails.py --message-id 18f3c2a1b9e --dry-run

Exit codes:
    0  Success (all messages archived, or dry-run completed)
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
# Core
# ─────────────────────────────────────────────

def archive_messages(service, message_ids: list, dry_run: bool) -> bool:
    """Remove the INBOX label from each message. Returns True if all succeeded."""
    success = 0
    errors = 0

    for msg_id in message_ids:
        prefix = "[DRY RUN] " if dry_run else ""
        try:
            if not dry_run:
                service.users().messages().modify(
                    userId="me",
                    id=msg_id,
                    body={"removeLabelIds": ["INBOX"]}
                ).execute()
            print(f"{prefix}Archived {msg_id}")
            success += 1
        except HttpError as e:
            print(f"ERROR: Could not archive message {msg_id}: {e}")
            errors += 1

    print(f"\nDone. {success} archived, {errors} failed.")
    return errors == 0


# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Archive Gmail messages (remove INBOX label) by message ID."
    )
    parser.add_argument(
        "--message-id", dest="message_ids", action="append", required=True, metavar="ID",
        help="Gmail message ID to archive. Repeat this flag for multiple messages."
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
    ok = archive_messages(service, args.message_ids, args.dry_run)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
