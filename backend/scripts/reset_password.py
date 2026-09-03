"""Reset an existing user's password.

Usage (no arguments needed — a password is generated and printed at the end):
    .venv/Scripts/python.exe scripts/reset_password.py

Optional flags:
    .venv/Scripts/python.exe scripts/reset_password.py --username admin --password "..."
"""
import argparse
import secrets
import string
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from app.database.connection import SessionLocal
from app.models.user import User
from app.security.password import hash_password


def generate_password(length: int = 14) -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--username", default="admin")
    parser.add_argument("--password", default=None)
    args = parser.parse_args()

    generated_password = args.password is None
    if generated_password:
        args.password = generate_password()

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == args.username).one_or_none()
        if user is None:
            print(f"user '{args.username}' not found")
            sys.exit(1)

        user.password_hash = hash_password(args.password)
        db.commit()

        print()
        print("=" * 50)
        print(f"  usuario:  {args.username}")
        print(f"  password: {args.password}")
        print("  (guardala, no se volvera a mostrar)")
        print("=" * 50)
    finally:
        db.close()


if __name__ == "__main__":
    main()
