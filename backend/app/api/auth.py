from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.user import Token, UserCreate, UserRead
from app.security.deps import get_current_user, require_roles
from app.services.auth_service import AuthService

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    token = AuthService(db).authenticate(form_data.username, form_data.password)
    return Token(access_token=token)


@router.post("/register", response_model=UserRead, status_code=201, dependencies=[Depends(require_roles("ADMIN"))])
def register(payload: UserCreate, db: Session = Depends(get_db)):
    user = AuthService(db).register(
        username=payload.username,
        email=payload.email,
        password=payload.password,
        first_name=payload.first_name,
        last_name=payload.last_name,
        role_codes=payload.role_codes,
    )
    return user


@router.get("/me", response_model=UserRead)
def me(current_user=Depends(get_current_user)):
    return current_user
