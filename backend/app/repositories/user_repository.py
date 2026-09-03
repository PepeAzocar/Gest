import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import Role, User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: uuid.UUID) -> User | None:
        return self.db.get(User, user_id)

    def get_by_username(self, username: str) -> User | None:
        stmt = select(User).where(User.username == username)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_roles_by_codes(self, codes: list[str]) -> list[Role]:
        if not codes:
            return []
        stmt = select(Role).where(Role.code.in_(codes))
        return list(self.db.execute(stmt).scalars().all())

    def create(self, user: User) -> User:
        self.db.add(user)
        self.db.flush()
        return user
