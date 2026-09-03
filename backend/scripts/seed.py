"""One-time seed: base roles + an initial ADMIN user.

Usage (no arguments needed — a password is generated and printed at the end):
    .venv/Scripts/python.exe scripts/seed.py

Optional flags let you override the defaults:
    .venv/Scripts/python.exe scripts/seed.py --username admin --email admin@example.com --password "..."
"""
import argparse
import secrets
import string
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from app.database.connection import SessionLocal
from app.models.user import Role, User
from app.security.password import hash_password


def generate_password(length: int = 14) -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))

BASE_ROLES = [
    ("ADMIN", "Administrador", "Acceso total al sistema"),
    ("SALES", "Ventas", "Productos, clientes y ventas"),
    ("WAREHOUSE", "Bodega", "Inventario y movimientos"),
    ("PRODUCTION", "Producción", "Fabricación y materiales"),
    ("READ_ONLY", "Solo lectura", "Consultas únicamente"),
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--username", default="admin")
    parser.add_argument("--email", default="admin@gest.app")
    parser.add_argument("--password", default=None)
    args = parser.parse_args()

    generated_password = args.password is None
    if generated_password:
        args.password = generate_password()

    db = SessionLocal()
    try:
        roles_by_code = {}
        for code, name, description in BASE_ROLES:
            role = db.query(Role).filter(Role.code == code).one_or_none()
            if role is None:
                role = Role(code=code, name=name, description=description)
                db.add(role)
                db.flush()
                print(f"role created: {code}")
            roles_by_code[code] = role

        if db.query(User).filter(User.username == args.username).one_or_none() is not None:
            print(f"user '{args.username}' already exists, skipping user creation")
        else:
            user = User(
                username=args.username,
                email=args.email,
                password_hash=hash_password(args.password),
                roles=[roles_by_code["ADMIN"]],
            )
            db.add(user)
            print(f"admin user created: {args.username}")

        db.commit()

        if generated_password:
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
