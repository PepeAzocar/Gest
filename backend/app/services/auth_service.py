from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.security.jwt import create_access_token
from app.security.password import hash_password, verify_password


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.users = UserRepository(db)

    def register(
        self,
        username: str,
        email: str,
        password: str,
        first_name: str | None,
        last_name: str | None,
        role_codes: list[str],
    ) -> User:
        if self.users.get_by_username(username):
            raise HTTPException(status.HTTP_409_CONFLICT, "El nombre de usuario ya existe")
        if self.users.get_by_email(email):
            raise HTTPException(status.HTTP_409_CONFLICT, "El correo ya está registrado")

        user = User(
            username=username,
            email=email,
            password_hash=hash_password(password),
            first_name=first_name,
            last_name=last_name,
            roles=self.users.get_roles_by_codes(role_codes),
        )
        self.users.create(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def authenticate(self, username: str, password: str) -> str:
        invalid_credentials = HTTPException(
            status.HTTP_401_UNAUTHORIZED, "Usuario o contraseña incorrectos"
        )

        user = self.users.get_by_username(username)
        if user is None or not verify_password(password, user.password_hash):
            raise invalid_credentials
        if not user.active:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Usuario inactivo")

        user.last_login = datetime.now(timezone.utc)
        self.db.commit()

        return create_access_token(user.id, [role.code for role in user.roles])
